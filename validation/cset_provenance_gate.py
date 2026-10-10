"""A source-identity gate over ORIGINAL workbook, not a causal/statistical test.
Official CAT methodological definitions are documented; row-level lineage is absent.
"""
import hashlib,json
from pathlib import Path
import pandas as pd
P=Path(__file__).resolve().parents[1]
def main():
    src=P/"data/raw/AI_Balanced_Panel (1).xlsx"
    d=pd.read_excel(src)
    assert len(d)==270 and d.ISO3.nunique()==30 and d.Year.nunique()==9
    assert not d.duplicated(["ISO3","Year"]).any()
    assert d[["AI_Investment","AI_Patents"]].notna().all().all()
    patents=d.pivot(index="ISO3",columns="Year",values="AI_Patents")
    invest=d.pivot(index="ISO3",columns="Year",values="AI_Investment")
    chinese_2024=int(patents.loc["CHN",2024])
    entire_2024=int(d.loc[d.Year.eq(2024),"AI_Patents"].sum())
    entire_2016_2024=int(d.AI_Patents.sum())
    assert (chinese_2024,entire_2024,entire_2016_2024)==(1044027,1133893,5316559)
    assert int(invest.loc["USA",2019])==134555
    ratio=chinese_2024/entire_2024
    # Anomaly detection MUST NOT invent source vintage, units, record definitions.
    assert ratio>0.9
    report={
       "original_workbook_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
       "countries":30,"rows":270,"start_year":2016,"end_year":2024,
       "patents_china_2023":int(patents.loc["CHN",2023]),
       "patents_china_2024":chinese_2024,
       "patents_all_countries_2024":entire_2024,
       "patents_china_share_2024":ratio,
       "patents_30_countries_2016_2024":entire_2016_2024,
       "investment_USA_2019_raw_units":int(invest.loc["USA",2019]),
       "official_cat_documented":{
        "investments":["companies_yearly_disclosed.disclosed_investment",
                       "companies_yearly_estimated.estimated_investment"],
        "official_units":"million USD for documented CAT metrics, NOT established for user's worksheet",
        "patents":"patents_yearly_applications.num_patent_applications; families/priority year/jurisdiction",
        "official_completeness_variable":"complete",
        "source_url":"https://eto.tech/dataset-docs/country-ai-activity-metrics/"
       },
       "gates":{
        "workbook_integrity":"PASS",
        "official_metric_identity":"UNRESOLVED",
        "matched_official_vintage":"UNRESOLVED",
        "investment_unit_in_workbook":"UNRESOLVED",
        "patent_family_vs_documents":"UNRESOLVED",
        "2024_official_complete_status":"UNRESOLVED",
        "row_level_official_reconciliation":"UNRESOLVED",
        "causal_validity":"NOT_APPROVED"
       }
    }
    (P/"outputs").mkdir(exist_ok=True)
    (P/"outputs/cset_provenance_gate.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print("CSET_PROVENANCE_DIAGNOSTICS",json.dumps({"China_2024":chinese_2024,"share":ratio,
       "all_years":entire_2016_2024,"source_approved":False}))
if __name__=="__main__":main()
