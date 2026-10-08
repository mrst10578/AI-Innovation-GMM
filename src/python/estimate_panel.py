"""Reproducible real-data exploratory panel models; all results marked observational."""
from pathlib import Path
import json, sys, warnings
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy.stats import norm

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"outputs"; OUT.mkdir(exist_ok=True)
VARS=["AI_Investment","AI_Patents","HighTech_Exports","Unemployment","GDP_Growth"]

def panel():
    d=pd.read_excel(ROOT/"data/raw/AI_Balanced_Panel (1).xlsx")
    assert {"ISO3","Year",*VARS}<=set(d.columns)
    assert not d.duplicated(["ISO3","Year"]).any()
    assert d.Year.between(2016,2024).all()
    d=d.sort_values(["ISO3","Year"]).copy()
    for c in VARS:
        d[c]=pd.to_numeric(d[c],errors="coerce")
    for c in ["AI_Investment","AI_Patents"]:
        assert (d[c].dropna()>=0).all(), f"Negative {c} prevents log1p"
    d["ln1p_invest"]=np.log1p(d.AI_Investment)
    d["ln1p_patent"]=np.log1p(d.AI_Patents)
    for col in ["HighTech_Exports","Unemployment"]:
        d["L1_"+col]=d.groupby("ISO3")[col].shift()
    return d

def vif_summary(d):
    x=d[["ln1p_invest","ln1p_patent","GDP_Growth"]].dropna()
    return {name:float(variance_inflation_factor(x.assign(intercept=1).values,i))
            for i,name in enumerate(["ln1p_invest","ln1p_patent","GDP_Growth"])}

def model_fit(d,outcome,period,spec):
    v=["ln1p_invest","ln1p_patent","GDP_Growth"]
    lag="L1_"+outcome
    dynamic="dynamic" in spec
    rhs=([lag] if dynamic else [])+v
    if "fe" in spec: rhs+=["C(ISO3)","C(Year)"]
    if "pooled" in spec: rhs+=["C(Year)"]
    keep=[outcome]+v+([lag] if dynamic else [])+["ISO3","Year"]
    x=d[d.Year<=period][keep].dropna().copy()
    n=len(x); countries=int(x.ISO3.nunique())
    if n<=20:return {"status":"too_few_observations","n":n}
    f=outcome+" ~ "+" + ".join(rhs)
    try:
        fit=smf.ols(f,data=x).fit(cov_type="cluster",cov_kwds={"groups":x.ISO3,
                                                                  "use_correction":True})
        termlist=([lag] if dynamic else [])+v
        co={t:{"estimate":float(fit.params[t]),"se":float(fit.bse[t]),
               "p":float(fit.pvalues[t]),"ci_low":float(fit.conf_int().loc[t,0]),
               "ci_high":float(fit.conf_int().loc[t,1])} for t in termlist}
        return {"status":"estimated_exploratory","model":outcome,"spec":spec,"period_end":period,
                "formula":f,"n":n,"countries":countries,"r_squared":float(fit.rsquared),
                "coefficients":co,"warning":"Observational OLS/FE; dynamic FE Nickell bias; no causal claim."}
    except Exception as e:return {"status":"estimation_failed","error":repr(e),"formula":f}

def cd_test(d,outcome,period):
    # Diagnostic on pooled two-way FE residuals, requires complete joint sample.
    x=d[d.Year<=period][["ISO3","Year",outcome,"ln1p_invest","ln1p_patent","GDP_Growth"]].dropna()
    if len(x)<20:return {"status":"not_run_insufficient_data"}
    fit=smf.ols(outcome+" ~ ln1p_invest+ln1p_patent+GDP_Growth+C(ISO3)+C(Year)",x).fit()
    x=x.copy();x["resid"]=fit.resid
    pivot=x.pivot(index="Year",columns="ISO3",values="resid").dropna(axis=1)
    n=pivot.shape[1];t=pivot.shape[0]
    corr=pivot.corr().to_numpy()
    r=corr[np.triu_indices(n,1)]
    if n<3 or t<4:return {"status":"invalid_short_sample"}
    cd=float(np.sqrt(2*t/(n*(n-1)))*np.nansum(r))
    return {"status":"exploratory_pesaran_cd_not_bias_corrected","statistic":cd,
            "p_approx":float(2*norm.sf(abs(cd))),"n_countries":int(n),
            "years":int(t),"method":"balanced pairwise correlations of static two-way FE residuals"}

def main():
    d=panel()
    # numeric panel ID for independent gretl; full data stay in Actions runner only.
    d["panel_id"]=pd.factorize(d["ISO3"])[0]+1
    d[["panel_id","ISO3","Year","ln1p_invest","ln1p_patent","HighTech_Exports","Unemployment","GDP_Growth"]].to_csv(ROOT/"data/processed/model_panel.csv",index=False)
    print("Python",sys.version.replace("\n"," "))
    print("Pandas",pd.__version__)
    print("Statsmodels",__import__("statsmodels").__version__)
    print("STUDY","rows",len(d),"countries",d.ISO3.nunique(),"years",d.Year.nunique())
    print("MISSING",d[VARS].isna().sum().to_dict())
    print("VIF",json.dumps(vif_summary(d)))
    desc=d[VARS].describe().round(5).to_dict()
    correlations=d[["ln1p_invest","ln1p_patent","GDP_Growth","HighTech_Exports","Unemployment"]].corr().round(5).to_dict()
    results={}
    for yr in [2024,2023]:
        for outcome in ["HighTech_Exports","Unemployment"]:
            for spec in ["static_pooled","static_fe","dynamic_pooled","dynamic_fe"]:
                key=f"{outcome}_{yr}_{spec}"
                results[key]=model_fit(d,outcome,yr,spec)
                print("ESTIMATION",key,json.dumps(results[key],ensure_ascii=False,allow_nan=False))
            cd=cd_test(d,outcome,yr)
            print("CROSS_SECTION_DEPENDENCE",outcome,yr,json.dumps(cd))
    summary={"method":"Real-data OLS with ISO3 clustered SE; descriptive not causal",
             "input":"data/raw/AI_Balanced_Panel (1).xlsx",
             "rows":len(d),"countries":int(d.ISO3.nunique()),
             "years":sorted(d.Year.unique().tolist()),
             "missing":d[VARS].isna().sum().astype(int).to_dict(),
             "vif_pooled_raw_regressors":vif_summary(d),
             "descriptive":desc,"correlations":correlations,"models":results}
    (OUT/"python_estimation.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False))
    # Aggregate only, do not publish row-level data in Actions artifacts.
    d.groupby("Year")[VARS].agg(["mean","median"]).to_csv(OUT/"annual_aggregates.csv")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        series=d.groupby("Year")[["AI_Patents","AI_Investment"]].median()
        for col in series:
            fig,ax=plt.subplots(figsize=(7,4))
            series[col].plot(ax=ax,marker="o")
            ax.set_title("Annual median: "+col); ax.set_xlabel("Year")
            ax.set_ylabel("Original unit: check source dictionary")
            fig.tight_layout();fig.savefig(OUT/("trend_"+col+".png"),dpi=170);plt.close(fig)
    except Exception as e: print("GRAPH_FAILED",repr(e))
    print("SUMMARY_WRITTEN",OUT/"python_estimation.json")
if __name__=="__main__":main()
