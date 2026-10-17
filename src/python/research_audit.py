"""Source-only audit and reproducible R input: never overwrite original Excel."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import pandas as pd
from src.python.preflight import ROOT, audit_dataframe

def main() -> int:
    cfg=json.loads((ROOT/"config/project.json").read_text(encoding="utf-8"))
    source=ROOT/"data/raw"/cfg["source_workbook"]
    output=ROOT/"outputs"
    processed=ROOT/"data/processed"
    output.mkdir(parents=True,exist_ok=True)
    processed.mkdir(parents=True,exist_ok=True)
    df=pd.read_excel(source,engine="openpyxl")
    audit=audit_dataframe(df,cfg)
    if audit["status"]!="ready_for_methodology_audit":
        raise RuntimeError(f"Input data did not pass basic audit: {audit}")
    df=df.sort_values(["ISO3","Year"]).reset_index(drop=True)
    patents=df.pivot(index="ISO3",columns="Year",values="AI_Patents")
    declining=patents.index[patents[2024]<patents[2023]].tolist()
    audit.update({
        "original_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "iran_in_sample":bool("IRN" in df.ISO3.values),
        "investment_zero_rows":int((df.AI_Investment==0).sum()),
        "patent_zero_rows":int((df.AI_Patents==0).sum()),
        "patent_2024_declining_country_count":len(declining),
        "patent_2024_declining_iso3":declining,
        "patent_country_totals_by_year":{str(k):int(v) for k,v in df.groupby("Year").AI_Patents.sum().items()},
        "data_source":str(source.relative_to(ROOT)),
        "limitations":[
            "2024 coverage/revision of patent applications cannot be verified from this workbook alone.",
            "AI investment nominal currency magnitude/comparability lacks primary-source verification.",
            "No Iranian observations; do not claim Iran peer group or causal effects.",
            "Unemployment is unemployment rate; HighTech_Exports is % of manufacturing exports."
        ]
    })
    if (df.AI_Investment<0).any() or (df.AI_Patents<0).any():
        raise ValueError("log1p transformations invalid for negative source counts")
    df["ln_ai_investment"]=(1+df.AI_Investment).apply(__import__("math").log)
    df["ln_ai_patents"]=(1+df.AI_Patents).apply(__import__("math").log)
    path=processed/"panel_for_r.csv"
    df.to_csv(path,index=False,float_format="%.15g")
    (output/"research_data_audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in audit.items() if k not in ("patent_2024_declining_iso3","patent_country_totals_by_year")},ensure_ascii=False,indent=2))
    print(f"R input: {path} (derived CSV; source untouched)")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
