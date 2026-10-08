"""Read only research-specific source documents and audit the panel. Never alters source files."""
from pathlib import Path
import json, hashlib, zipfile, xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"sources"
RAW=ROOT/"data/raw/AI_Balanced_Panel (1).xlsx"
OUT=ROOT/"outputs"; OUT.mkdir(exist_ok=True)
def source_hash(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def docx_paragraphs(p):
    with zipfile.ZipFile(p) as z:
        root=ET.fromstring(z.read("word/document.xml"))
    ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    return ["".join(t.text or "" for t in par.findall(".//w:t",ns))
            for par in root.findall(".//w:p",ns)]
def clean(x):
    return x.item() if isinstance(x,np.generic) else x

def main():
    print("=== RESEARCH SOURCE AUDIT ===")
    sources={}
    for p in sorted(SRC.iterdir()):
        if p.is_file():
            sources[p.name]={"sha256":source_hash(p),"bytes":p.stat().st_size}
            print("SOURCE",p.name,"sha256",sources[p.name]["sha256"])
    manuscript=list(SRC.glob("*.docx"))
    if manuscript:
        lines=[s for s in docx_paragraphs(manuscript[0]) if s.strip()]
        (OUT/"manuscript_extracted.txt").write_text("\n".join(lines),encoding="utf-8")
        print("=== MANUSCRIPT (FIRST 200 PARAGRAPHS) ===")
        for i,line in enumerate(lines[:200],1):print("MANUSCRIPT",i,line[:650])
        print("MANUSCRIPT_PARAGRAPHS",len(lines))
    else:print("MISSING WORD MANUSCRIPT")
    dictionaries=list(SRC.glob("*Dictionary*.xlsx"))
    for dictionary in dictionaries:
        sheets=pd.read_excel(dictionary,sheet_name=None,header=None)
        for name,df in sheets.items():
            print("=== DICTIONARY",name,df.shape,"===")
            for row in df.fillna("").head(80).itertuples(index=False,name=None):
                print("DICTIONARY_ROW",json.dumps([str(v)[:150] for v in row],ensure_ascii=False))
    df=pd.read_excel(RAW)
    print("DATA_COLUMNS",json.dumps(list(df.columns),ensure_ascii=False))
    print("DATA_SHAPE",df.shape,"YEARS",sorted(df.Year.dropna().unique().tolist()),
          "COUNTRIES",df.ISO3.nunique(),"DUPES",df.duplicated(["ISO3","Year"]).sum())
    print("DATA_TYPES",df.dtypes.astype(str).to_dict())
    print("DATA_MISSING",df.isna().sum().to_dict())
    print("DATA_ISO3",sorted(df.ISO3.unique().tolist()))
    print("NUMERIC_DESCRIBE",df.describe().round(3).to_json(orient="index",force_ascii=False))
    for c in ["AI_Investment","AI_Patents","HighTech_Exports","GDP_Growth","Unemployment"]:
        v=pd.to_numeric(df[c],errors="coerce")
        print("VARIABLE",c,"negative",int((v<0).sum()),"zero",int((v==0).sum()),
              "missing",int(v.isna().sum()),"min",v.min(),"max",v.max())
    pv=df.pivot(index="ISO3",columns="Year",values="AI_Patents")
    if 2024 in pv and 2023 in pv:
        delta=pv[2024]-pv[2023]
        print("PATENTS_2024",json.dumps({"declines":int((delta<0).sum()),
              "increases":int((delta>0).sum()),"unchanged":int((delta==0).sum()),
              "total_2023":float(pv[2023].sum()),"total_2024":float(pv[2024].sum()),
              "median_country_change":float(delta.median()),"countries_declining":delta[delta<0].index.tolist()},ensure_ascii=False))
    years=df.groupby("Year")[["AI_Investment","AI_Patents","HighTech_Exports","Unemployment"]].agg(["mean","median","sum"])
    print("YEAR_SUMMARY",years.round(3).to_json(force_ascii=False))
    print("=== END SOURCE AUDIT ===")
    (OUT/"research_source_audit.json").write_text(json.dumps({"sources":sources,
             "rows":len(df),"countries":int(df.ISO3.nunique()),
             "duplicate_keys":int(df.duplicated(["ISO3","Year"]).sum()),
             "missing":df.isna().sum().to_dict()},ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__": main()
