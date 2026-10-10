"""Cross-reference two pinned OFFICIAL ETO CAT releases without guessing metric or unit.
Runs only when actual Zenodo archives have been downloaded. Never silently
substitute approximate values, renamed countries, or unrelated CSET vintage.
"""
import csv, hashlib, io, json, re, sys, zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
REQUIRED=("patents_yearly_applications","companies_yearly_disclosed","companies_yearly_estimated")
def top_level_field(s):
    return str(s).strip().lower() in ("all ai","all ai fields","ai","artificial intelligence",
                                      "all artificial intelligence","all fields","all")
def cn(s):
    s=str(s).strip().lower()
    return re.sub(r"[^a-z]","",s)
def sample(rows,column,year,country):
    candidates=[r for r in rows if str(r.get("year","")).strip()==str(year)
                and (cn(r.get("country",""))==cn(country) or
                     (country=="China" and cn(r.get("country","")).startswith("china")))]
    groups=sorted({str(r.get("field","")) for r in candidates})
    chosen=[r for r in candidates if top_level_field(r.get("field"))]
    if len(chosen)!=1:
        return {"match_status":"UNVERIFIED_LEVEL_OR_COVERAGE","available_fields":groups[:35],
                "matching_rows":len(candidates),"unambiguously_matching_all_ai_rows":len(chosen)}
    row=chosen[0]
    try: official=float(row[column])
    except (KeyError,ValueError,TypeError):
        return {"match_status":"NO_VALID_NUMERIC_OFFICIAL_VALUE","field":row.get("field")}
    return {"match_status":"EXACT_OFFICIAL_VERSION_OBSERVATION_ONLY",
            "field":row.get("field"),"official_value":official,"year":year,
            "country":row.get("country"),"complete":row.get("complete"),
            "documented_unit":"million_USD" if "investment" in column else "patent_families"}
def one(zpath):
    assert zpath.is_file(),zpath
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        names=z.namelist(); summaries={}; data={}
        for key in REQUIRED:
            matches=[n for n in names if n.lower().split("/")[-1]==key+".csv"]
            if len(matches)!=1:
                summaries[key]={"status":"CSV_NAME_NOT_UNIQUE_OR_ABSENT",
                                "match_count":len(matches)}
                continue
            content=z.read(matches[0]).decode("utf-8-sig")
            rr=csv.DictReader(io.StringIO(content))
            rows=list(rr)
            data[key]=rows
            summaries[key]={"file":matches[0],"rows":len(rows),"columns":rr.fieldnames,
                            "fields_sample":sorted(set(r.get("field","") for r in rows))[:45]}
        result={"archive":zpath.name,"zip_sha256":hashlib.sha256(zpath.read_bytes()).hexdigest(),
                "entries":len(names),"tables":summaries,"observations":{}}
        if "patents_yearly_applications" in data:
            for yr in (2023,2024):
                result["observations"][f"patents_CHN_{yr}"]=sample(
                    data["patents_yearly_applications"],"num_patent_applications",yr,"China")
        for k in ("companies_yearly_disclosed","companies_yearly_estimated"):
            if k in data:
                m="disclosed_investment" if "disclosed" in k else "estimated_investment"
                result["observations"][f"{k}_USA_2019"]=sample(data[k],m,2019,"United States")
        # **Never** assert that a CAT vintage equals the source workbook by default.
        result["source_workbook_identity"]="NOT_PROVEN_UNLESS_COUNTRY_YEAR_AND_METRIC_RECONCILED"
        return result
def main():
    files=[Path(p) for p in sys.argv[1:]]
    assert files,"Usage: compare_official_cat.py downloaded-official-cat*.zip"
    outputs=[one(p) for p in files]
    (BASE/"outputs").mkdir(exist_ok=True)
    dest=BASE/"outputs/cset_cat_official_vintage_comparison.json"
    dest.write_text(json.dumps({"snapshots":outputs,
           "workbook_reference":{"CHN_patents_2023":783813,"CHN_patents_2024":1044027,
                                 "USA_investment_2019":134555,"units":"UNVERIFIED"},
           "official_equals_workbook":"NOT_ESTABLISHED",
           "exact_source_version_verified":False},ensure_ascii=False,indent=2))
    for o in outputs:
        print("CAT_OFFICIAL_SNAPSHOT",o["archive"],o["zip_sha256"],
              "tables_found",list(k for k,v in o["tables"].items() if "rows" in v))
        print("CSET_CROSSCHECK_VALUES",json.dumps(o["observations"]))
    print("METRIC_IDENTITY_GATE=UNRESOLVED; no fabrication or source-unit substitution")
if __name__=="__main__":main()
