"""Read-only comparison against current World Bank WDI API (no source substitutions).

Three source series as documented in the original dictionary:
 TX.VAL.TECH.MF.ZS, NY.GDP.MKTP.KD.ZG, SL.UEM.TOTL.ZS.
Only the 30 supplied ISO3 countries and 2016-2024 are queried.
On network failure, fail loudly without inventing WDI observations.
Usage: python -m src.python.verify_wdi_reference
"""
from __future__ import annotations

import csv
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
API = "https://api.worldbank.org/v2"
SOURCES = {
    "HighTech_Exports": "TX.VAL.TECH.MF.ZS",
    "GDP_Growth": "NY.GDP.MKTP.KD.ZG",
    "Unemployment": "SL.UEM.TOTL.ZS",
}
EXPECTED_SHA = "4f9bf76658d1f495d3eb3e39b226bb5ba6ac39446b35e41bfce4a2aab65d0434"

def compare(*, strict: bool = True) -> tuple[dict,list[dict]]:
    path = ROOT/"data/raw/AI_Balanced_Panel (1).xlsx"
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA:
        raise RuntimeError("Original supplied panel hash changed; provenance check aborted.")
    data = pd.read_excel(path,engine="openpyxl")
    assert data.shape == (270,7) and not data.duplicated(["ISO3","Year"]).any()
    countries = sorted(data.ISO3.unique())
    assert len(countries) == 30 and set(data.Year) == set(range(2016,2025))
    iso3 = ";".join(countries)
    rows=[]
    aggregate={}
    sample_time = datetime.now(timezone.utc).isoformat()
    for source_col, indicator in SOURCES.items():
        params = urllib.parse.urlencode({
            "format": "json", "date": "2016:2024", "per_page": "20000"
        })
        url = f"{API}/country/{iso3}/indicator/{indicator}?{params}"
        req = urllib.request.Request(url,headers={"User-Agent":"AI-Innovation-GMM-research-source-audit/1.0"})
        with urllib.request.urlopen(req,timeout=30) as res:
            response = json.load(res)
        if not isinstance(response,list) or len(response)<2 or not isinstance(response[1],list):
            raise RuntimeError(f"Bad WDI payload for {indicator}")
        meta,items=response
        if int(meta["pages"]) != 1:
            raise RuntimeError(f"Unexpected WDI pagination: {indicator}")
        lookup={}
        for entry in items:
            code=entry.get("countryiso3code")
            if code not in countries:continue
            year=int(entry["date"])
            key=code,year
            if key in lookup:
                raise RuntimeError(f"Duplicate WDI record: {indicator}: {key}")
            lookup[key]=entry
        for p in data.itertuples(index=False):
            key=p.ISO3,int(p.Year)
            ref=lookup.get(key)
            value=ref["value"] if ref is not None else None
            val=float(getattr(p,source_col))
            refnum=None if value is None else float(value)
            deviation=None if refnum is None else val-refnum
            rows.append({
                "source_col":source_col,"wdi_code":indicator,"ISO3":key[0],"Year":key[1],
                "original_supplied_value":val,
                "wdi_reference_value":"" if refnum is None else refnum,
                "original_minus_reference":"" if deviation is None else deviation,
                "absolute_deviation":"" if deviation is None else abs(deviation),
                "equal_to_0.001":"" if deviation is None else abs(deviation)<=0.001,
                "reference_obs_status": "" if ref is None else (ref.get("obs_status") or ""),
                "reference_lastupdated":meta.get("lastupdated",""),
                "reference_indicator_name": "" if ref is None else ref["indicator"]["value"]
            })
        subset=[r for r in rows if r["source_col"]==source_col]
        mismatched=[r for r in subset if r["equal_to_0.001"] is False]
        missing=[r for r in subset if r["equal_to_0.001"] == ""]
        aggregate[source_col]={
            "wdi_indicator":indicator,
            "reference_lastupdated":meta.get("lastupdated"),
            "wdi_observations_in_scope": len(lookup),
            "original_rows":270,
            "matches_within_0.001":sum(r["equal_to_0.001"] is True for r in subset),
            "differences_above_0.001":len(mismatched),
            "missing_reference_observations":len(missing),
            "max_abs_difference":max((r["absolute_deviation"] for r in subset if r["absolute_deviation"]!=""),default=None),
            "differences": [{
                "ISO3":r["ISO3"],"Year":r["Year"],
                "original":r["original_supplied_value"],
                "updated_WDI_reference":r["wdi_reference_value"],
                "absolute_deviation":r["absolute_deviation"]
            } for r in mismatched]
        }
    report={
        "audit_time_utc":sample_time,
        "original_sha256":sha,
        "original_rows":270,
        "countries":countries,
        "reference_api":"https://api.worldbank.org/v2",
        "method":"read_only; exact 30-country/9-year ISO3 matching; tolerance absolute 0.001; no data replacement",
        "email_received":"2026-09-30",
        "special_notice":"WDI online latest update can postdate original sender's email. Numeric discrepancies may represent revision OR original error: cause not established.",
        "source_results":aggregate
    }
    if strict and any(v["missing_reference_observations"]>0 for v in aggregate.values()):
        raise RuntimeError("Current WDI API has missing values for original panel; report cannot claim full comparison")
    return report,rows

def main():
    report,rows=compare()
    dest=ROOT/"reports"
    dest.mkdir(exist_ok=True)
    (dest/"WDI_REFERENCE_RECONCILIATION_20261017.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (dest/"WDI_REFERENCE_ROW_COMPARISON_20261017.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for col,v in report["source_results"].items():
        print(col,v["wdi_indicator"],"matches",v["matches_within_0.001"],
              "different",v["differences_above_0.001"],"missing",v["missing_reference_observations"],
              "lastupdated",v["reference_lastupdated"])
    print("Saved 810 individual comparison records without changing the original panel.")

if __name__=="__main__":main()
