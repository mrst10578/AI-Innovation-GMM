"""Check full original panel and 2024 concentration; no CSET scraping or invented source vintage."""
from pathlib import Path
import json,hashlib,pandas as pd
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=ROOT/"data/raw/AI_Balanced_Panel (1).xlsx"
    source=ROOT/"sources/AI_Balanced_Panel (1).xlsx"
    assert sha(p)==sha(source),"Workbook source copies differ"
    d=pd.read_excel(p).sort_values(["ISO3","Year"])
    assert len(d)==270 and d.ISO3.nunique()==30 and d.Year.nunique()==9
    assert not d.duplicated(["ISO3","Year"]).any()
    assert not d.isna().any().any()
    w=d.pivot(index="ISO3",columns="Year",values="AI_Patents")
    delta=(w[2024]-w[2023]).sort_values(ascending=False)
    total=int(delta.sum())
    r={"source_sha256":sha(p),"source_duplicates_identical":True,
       "observations":int(len(d)),"countries":int(d.ISO3.nunique()),
       "year_2024":{"declines":int((delta<0).sum()),"increases":int((delta>0).sum()),
         "total_2023":int(w[2023].sum()),"total_2024":int(w[2024].sum()),
         "median_country_change":float(delta.median()),"aggregate_change":total,
         "country_delta_sorted":[{"country":str(k),"delta":int(v),
          "fraction_of_aggregate_change":float(v/total) if total else None}
           for k,v in delta.items()]},
       "investment_2019_original_unit":{str(k):float(v) for k,v in d.loc[d.Year.eq(2019),["ISO3","AI_Investment"]].values},
       "source_gates":{"AI_Investment_unit":"UNKNOWN exact USD multiplier and category",
                       "AI_Patents_time_basis":"UNKNOWN filing/priority/publication calendar",
                       "AI_Patents_geography":"UNKNOWN priority/office/inventor affiliation",
                       "CSET_extract_vintage":"UNKNOWN",
                       "2024_delay":"UNPROVEN hypothesis"}}
    (ROOT/"outputs").mkdir(exist_ok=True)
    (ROOT/"outputs/source_forensics.json").write_text(json.dumps(r,ensure_ascii=False,indent=2))
    print("PATENT_FORENSICS_2024",json.dumps(r["year_2024"]))
    print("INVESTMENT_USA_2019_ORIGINAL_UNIT",r["investment_2019_original_unit"].get("USA"))
    print("CSET_PROVENANCE_NOT_CERTIFIED")
if __name__=="__main__":main()
