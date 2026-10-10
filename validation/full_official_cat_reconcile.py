"""Evidence-preserving full-panel comparison with PINNED official ETO CAT archives.

This is NOT a replacement for original workbook lineage: mismatching a release
only proves a mismatch with that release/metric. Missing CAT rows stay MISSING.
Uses only Python stdlib to extract the unmodified original XLSX.
"""
import csv
import hashlib
import io
import json
import math
import re
import statistics
import sys
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
SHEET_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
FIELDS = {
    "patents_yearly_applications": ("AI_Patents", "num_patent_applications", "families_first_filing_office_and_year"),
    "companies_yearly_disclosed": ("AI_Investment", "disclosed_investment", "million_USD_OFFICIAL_NOT_WORKBOOK"),
    "companies_yearly_estimated": ("AI_Investment", "estimated_investment", "million_USD_OFFICIAL_NOT_WORKBOOK"),
}
ALIASES = {
    "AUS": ["Australia"], "AUT": ["Austria"], "BEL": ["Belgium"],
    "CAN": ["Canada"], "CHE": ["Switzerland"], "CHN": ["China (mainland)", "China", "Mainland China"],
    "DEU": ["Germany"], "DNK": ["Denmark"], "ESP": ["Spain"],
    "FIN": ["Finland"], "FRA": ["France"], "GBR": ["United Kingdom", "UK"],
    "GRC": ["Greece"], "HUN": ["Hungary"], "IND": ["India"],
    "ISR": ["Israel"], "ITA": ["Italy"], "JPN": ["Japan"],
    "KOR": ["South Korea", "Korea, Republic of", "Republic of Korea", "Korea (South)"],
    "LUX": ["Luxembourg"], "MEX": ["Mexico"], "NLD": ["Netherlands", "The Netherlands"],
    "NOR": ["Norway"], "POL": ["Poland"], "PRT": ["Portugal"],
    "ROU": ["Romania"], "SWE": ["Sweden"], "TUR": ["Türkiye", "Turkiye", "Turkey"],
    "USA": ["United States", "United States of America", "USA"],
    "ZAF": ["South Africa"],
}
def canonical(s):
    s=unicodedata.normalize("NFKD",str(s))
    return re.sub("[^a-z0-9]","",s.encode("ascii","ignore").decode("ascii").lower())
def workbook_rows(path):
    with zipfile.ZipFile(path) as z:
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared=["".join(t.text or "" for t in node.iterfind(".//m:t", SHEET_NS))
                    for node in root.findall("m:si",SHEET_NS)]
        root=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        rows=[]
        for row in root.findall(".//m:sheetData/m:row",SHEET_NS):
            cells={}
            for cell in row.findall("m:c",SHEET_NS):
                ref=cell.attrib["r"]
                column=re.match("[A-Z]+",ref).group()
                v=cell.find("m:v",SHEET_NS)
                if cell.attrib.get("t")=="inlineStr":
                    val="".join(t.text or "" for t in cell.iterfind(".//m:t",SHEET_NS))
                elif v is None:
                    val=""
                elif cell.attrib.get("t")=="s":
                    val=shared[int(v.text)]
                elif cell.attrib.get("t") in ("str","e"):
                    val=v.text or ""
                else:
                    val=float(v.text) if v.text else ""
                cells[column]=val
            if cells: rows.append(cells)
        assert len(rows)==271 and rows[0]["A"]=="ISO3"
        assert [rows[0].get(x) for x in "ABCDEFG"] == [
            "ISO3","Year","AI_Investment","AI_Patents",
            "HighTech_Exports","GDP_Growth","Unemployment"]
        data=[]
        for row in rows[1:]:
            data.append({"ISO3":str(row["A"]).strip(),"Year":int(row["B"]),
                         "AI_Investment":float(row["C"]),"AI_Patents":float(row["D"]),
                         "HighTech_Exports":float(row["E"]),
                         "GDP_Growth":float(row["F"]),
                         "Unemployment":float(row["G"])})
        assert len(data)==270 and len({(d["ISO3"],d["Year"]) for d in data})==270
        assert set(d["ISO3"] for d in data)==set(ALIASES)
        assert set(d["Year"] for d in data)==set(range(2016,2025))
        return data

def read_table(z, key):
    paths=[p for p in z.namelist() if p.split("/")[-1].lower()==key+".csv"]
    if len(paths)!=1:
        return {"status":"MISSING_OR_MULTIPLE_CSV","paths":paths},None
    stream=io.StringIO(z.read(paths[0]).decode("utf-8-sig"))
    reader=csv.DictReader(stream)
    rows=[r for r in reader if (r.get("field") or "").strip()=="All"]
    assert rows,"No field=All rows in real official source"
    by_country={}
    for row in rows:
        country=canonical(row.get("country",""))
        by_country.setdefault(country,[]).append(row)
    return {"path":paths[0],"all_field_rows":len(rows),"countries":len(by_country)},by_country

def reconcile(data,archive,key,meta,by_country):
    source_var,official_var,documented_unit=FIELDS[key]
    detected={}
    if by_country is not None:
        for iso, aliases in ALIASES.items():
            matches=[c for c in by_country if c in {canonical(a) for a in aliases}]
            if len(matches)==1: detected[iso]=matches[0]
            elif len(matches)>1:
                raise AssertionError("Ambiguous explicit country aliases "+iso+" "+str(matches))
    details=[]
    for row in data:
        iso=row["ISO3"];year=row["Year"]
        known_country=detected.get(iso)
        candidates=[r for r in by_country[known_country] if str(r["year"]).strip()==str(year)] if known_country else []
        if len(candidates)>1: raise AssertionError("Duplicate country/field/year "+str((archive,key,iso,year)))
        original=row[source_var]
        outcome={"snapshot":archive,"series":key,"ISO3":iso,"Year":year,
                 "workbook_value":original,"official_value":"",
                 "official_complete":"","country_matched":bool(known_country),
                 "official_country":candidates[0]["country"] if candidates else "",
                 "status":"SOURCE_YEAR_MISSING"}
        if candidates:
            c=candidates[0]
            outcome["official_complete"]=(c.get("complete") or "").lower()
            try:
                v=float(c[official_var])
                assert math.isfinite(v)
                outcome["official_value"]=v
                outcome["status"]="EXACT_MATCH" if math.isclose(v,original,rel_tol=1e-9,abs_tol=1e-8) else "MISMATCH"
                outcome["ratio_workbook_over_official"]=original/v if v else None
            except (ValueError,TypeError,KeyError):
                outcome["status"]="OFFICIAL_VALUE_ABSENT"
        details.append(outcome)
    comparable=[x for x in details if x["status"] in ("EXACT_MATCH","MISMATCH")]
    ratios=[x["ratio_workbook_over_official"] for x in comparable
            if x.get("ratio_workbook_over_official") is not None and math.isfinite(x["ratio_workbook_over_official"])]
    incomplete=sum(x["official_complete"]=="false" for x in comparable)
    byyear={}
    for year in range(2016,2025):
        y=[x for x in details if x["Year"]==year]
        byyear[str(year)]={"matched":sum(x["status"]=="EXACT_MATCH" for x in y),
                      "mismatched":sum(x["status"]=="MISMATCH" for x in y),
                      "unavailable":sum(x["status"] not in ("EXACT_MATCH","MISMATCH") for x in y),
                      "official_incomplete":sum(x["official_complete"]=="false" for x in y)}
    stats={"archive":archive,"series":key,"official_unit":documented_unit,
           "workbook_unit":"UNRESOLVED" if source_var=="AI_Investment" else "COUNTS_DEFINITION_UNRECONCILED",
           "country_names_resolved":len(detected),"country_names_unresolved":sorted(set(ALIASES)-set(detected)),
           "panel_rows":len(details),"comparable_rows":len(comparable),
           "exact_matches":sum(x["status"]=="EXACT_MATCH" for x in details),
           "mismatched_rows":sum(x["status"]=="MISMATCH" for x in details),
           "unavailable_rows":len(details)-len(comparable),
           "incomplete_official_rows_among_comparable":incomplete,
           "ratio_median_workbook_over_official_nonzero":statistics.median(ratios) if ratios else None,
           "year_by_year":byyear,
           "has_original_extract_proof":False,
           "accept_source_lineage":False}
    assert stats["exact_matches"]+stats["mismatched_rows"]+stats["unavailable_rows"]==270
    return stats,details

def main(paths):
    assert paths,"Usage: python validation/full_official_cat_reconcile.py references/cat-*.zip"
    original=BASE/"data/raw/AI_Balanced_Panel (1).xlsx"
    wb=workbook_rows(original)
    outputs=[];rows=[]
    for filename in paths:
        p=Path(filename)
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
            item={"archive":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"series":{}}
            for key in FIELDS:
                meta,mapping=read_table(z,key)
                if mapping is None:
                    item["series"][key]={"status":meta["status"]}
                    continue
                stat,detail=reconcile(wb,p.name,key,meta,mapping)
                item["series"][key]=stat
                rows.extend(detail)
            outputs.append(item)
    (BASE/"outputs").mkdir(exist_ok=True)
    dest=BASE/"outputs/cset_full_official_reconciliation.json"
    dest.write_text(json.dumps({"original_source_sha256":hashlib.sha256(original.read_bytes()).hexdigest(),
          "snapshots":outputs,"identity_gate":"UNPROVEN","causal_claims_approved":False},
          indent=2,ensure_ascii=False),encoding="utf-8")
    fields=["snapshot","series","ISO3","Year","workbook_value","official_value","official_complete",
          "country_matched","official_country","status","ratio_workbook_over_official"]
    with (BASE/"outputs/cset_full_official_reconciliation.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader();writer.writerows(rows)
    for item in outputs:
        for series,stat in item["series"].items():
            print("OFFICIAL_FULL_PANEL_RECONCILIATION",item["archive"],series,
                  json.dumps({k:stat.get(k) for k in ("country_names_resolved","comparable_rows","exact_matches",
                     "mismatched_rows","unavailable_rows","incomplete_official_rows_among_comparable",
                     "ratio_median_workbook_over_official_nonzero","status")}))
    print("DO_NOT_IMPUTE_OR_MERGE_SOURCE_ROWS; provenance remains unverified")
if __name__=="__main__":
    main(sys.argv[1:])
