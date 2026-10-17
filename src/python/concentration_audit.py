"""Reproducible original-source concentration audit (never overwrite research data)."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import pandas as pd
from src.python.preflight import ROOT

def audit_concentration() -> dict:
    original = ROOT / "data/raw/AI_Balanced_Panel (1).xlsx"
    df=pd.read_excel(original,engine="openpyxl")
    assert df.shape[0]==270 and df.ISO3.nunique()==30
    assert not df.duplicated(["ISO3","Year"]).any()
    metrics = {}
    for measure in ("AI_Patents","AI_Investment"):
        pivot = df.pivot(index="ISO3",columns="Year",values=measure)
        years = {}
        for yr in sorted(pivot.columns):
            col=pivot[yr]
            total=float(col.sum())
            if total<=0: raise ValueError("Nonpositive aggregate measurement")
            shares=(col/total)
            years[str(yr)]={
                "total": total, "largest_country":str(col.idxmax()),
                "largest_country_value": float(col.max()),
                "largest_country_share":float(shares.max()),
                "top3_country_share":float(shares.nlargest(3).sum()),
                "hhi":float((shares**2).sum())
            }
        a,b=pivot[2023],pivot[2024]
        country_diff=(b-a).sort_values(ascending=False)
        metrics[measure]={
            "by_year":years, "country_growth_2024":{str(k):float(v) for k,v in country_diff.items()},
            "total_2023":float(a.sum()),"total_2024":float(b.sum()),
            "net_change_2024":float(country_diff.sum()),
            "country_declines_2024":int((country_diff<0).sum()),
            "country_increases_2024":int((country_diff>0).sum())
        }
    return {
        "input_sha256":hashlib.sha256(original.read_bytes()).hexdigest(),
        "source":"data/raw/AI_Balanced_Panel (1).xlsx",
        "scope":"Descriptive within-supplied-sample arithmetic only, not validated official country aggregates",
        "n_countries":30,"n_years":9,"n_rows":270,
        "metrics":metrics,
        "scientific_warnings":[
            "Concentration can create influential leverage in lagged GMM regressors and affects interpretation of pooled trends.",
            "A source coverage or revision artifact is possible but not proven by this dataset.",
            "Leave-country-out GMM tests do not establish causal identification or solve nominal measurement comparability."
        ]
    }

if __name__=="__main__":
    dest=ROOT/"reports/source_concentration_20261017.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    result=audit_concentration()
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    for v in result["metrics"]:
        row=result["metrics"][v]
        print(v,"total 2023",row["total_2023"],"total 2024",row["total_2024"],
              "2024 largest share",row["by_year"]["2024"]["largest_country_share"],
              "2024 decreasing countries",row["country_declines_2024"])
    print("SAVED",dest)
