"""Shared exact non-logged panel transform for R and gretl runs; no source mutation."""
from pathlib import Path
import numpy as np
import pandas as pd
root=Path(__file__).resolve().parents[2]
d=pd.read_excel(root/"data/raw/AI_Balanced_Panel (1).xlsx")
assert not d.duplicated(["ISO3","Year"]).any()
assert d.AI_Investment.ge(0).all() and d.AI_Patents.ge(0).all()
d=d.sort_values(["ISO3","Year"]).copy()
d["ln1p_invest"]=np.log1p(d.AI_Investment)
d["ln1p_patent"]=np.log1p(d.AI_Patents)
d["panel_id"]=pd.factorize(d.ISO3)[0]+1
out=root/"data/processed/model_panel.csv";out.parent.mkdir(exist_ok=True,parents=True)
d[["panel_id","ISO3","Year","ln1p_invest","ln1p_patent","HighTech_Exports","Unemployment","GDP_Growth"]].to_csv(out,index=False)
print("VALIDATED_PANEL_ROWS",len(d),"COUNTRIES",d.ISO3.nunique(),"YEARS",d.Year.nunique(),"CSV_SOURCE_NONPUBLIC_ARTIFACT")
