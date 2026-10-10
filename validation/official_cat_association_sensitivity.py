"""Separate 2026 v1.12.0 CAT-source-attributed FE sensitivity on real data.

NOT re-identification or repair of the user's original AI columns, and NOT GMM.
Predicators use official ETO CAT field=All metrics at pinned SHA256; outcomes
and GDP are taken from the original user's workbook, whose WDI row-level
provenance has NOT been independently re-downloaded. Preserve those facts.
"""
import csv, hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.stats import t as student_t
from validation.full_official_cat_reconcile import workbook_rows

ROOT=Path(__file__).resolve().parents[1]
PANEL=ROOT/"data/raw/AI_Balanced_Panel (1).xlsx"
CROSSWALK=ROOT/"outputs/cset_full_official_reconciliation.csv"
OUT_CSV=ROOT/"outputs/official_cat_fe_exploratory.csv"
OUT_JSON=ROOT/"outputs/official_cat_fe_qc.json"
SNAPSHOT="cat-zenodo-22772306-v1.12.0.zip"
OFFICIAL_ARCHIVE_SHA256="499647c0e1d55cdf5fca0c16ebc0d329bcbe99e1d4ca2578055d7c5c035256d5"
SERIES={"patents_yearly_applications":"patents",
        "companies_yearly_disclosed":"investment_disclosed",
        "companies_yearly_estimated":"investment_estimated"}
YCOLS=("HighTech_Exports","Unemployment")
REGRESSORS=("log1p_invest","log1p_patents","GDP_Growth")

def load():
    original=workbook_rows(PANEL)
    assert len(original)==270
    originals={(r["ISO3"],r["Year"]):r for r in original}
    raw=list(csv.DictReader(CROSSWALK.open(newline="",encoding="utf-8")))
    selected=[r for r in raw if r["snapshot"]==SNAPSHOT]
    assert len(selected)==810, f"Expected exactly 270 x 3 source rows, received {len(selected)}"
    seen=set()
    official={}
    for line in selected:
        key=(line["ISO3"],int(line["Year"]))
        label=SERIES.get(line["series"])
        assert label is not None and key in originals
        pair=(key,label)
        assert pair not in seen, "Official source duplicate detected"
        seen.add(pair)
        assert line["country_matched"]=="True"
        assert line["status"] in ("MISMATCH","EXACT_MATCH")
        v=float(line["official_value"])
        assert math.isfinite(v) and v>=0,"Negative or invalid logged official predictor"
        complete=str(line["official_complete"]).lower()
        assert complete in ("true","false"),"Incomplete-year marker missing"
        official.setdefault(key,{})[label]=v
        official[key][label+"_complete"]=complete=="true"
    assert len(official)==270
    assert all(len(x)==6 for x in official.values()),"Missing source metrics/complete flags"
    merged=[{**r,**official[(r["ISO3"],r["Year"])]} for r in original]
    assert len({(r["ISO3"],r["Year"]) for r in merged})==270
    return merged

def fit(rows,y,investment):
    # Design: 1 intercept, 3 within-country predictors, N-1 fixed country effects,
    # T-1 fixed year effects. All columns and cluster labels deterministic.
    rows=sorted(rows,key=lambda r:(r["ISO3"],r["Year"]))
    countries=sorted({r["ISO3"] for r in rows})
    years=sorted({r["Year"] for r in rows})
    X=[];Y=[]
    for r in rows:
        predictors=[math.log1p(r[investment]),math.log1p(r["patents"]),
                    r["GDP_Growth"]]
        row=[1.0,*predictors]
        row += [1.0 if r["ISO3"]==c else 0.0 for c in countries[1:]]
        row += [1.0 if r["Year"]==yr else 0.0 for yr in years[1:]]
        X.append(row);Y.append(r[y])
    x=np.asarray(X,dtype=float)
    target=np.asarray(Y,dtype=float)
    assert np.isfinite(x).all() and np.isfinite(target).all()
    n,k=x.shape;g=len(countries)
    assert n>k+g and g in (29,30)
    beta,residuals,rank,ss=np.linalg.lstsq(x,target,rcond=None)
    assert rank==k, f"Non-full-rank model: rank={rank} regressors={k}"
    e=target-x@beta
    inv=np.linalg.inv(x.T@x)
    meat=np.zeros((k,k))
    for c in countries:
        inds=np.array([r["ISO3"]==c for r in rows],dtype=bool)
        score=x[inds].T@e[inds]
        meat+=np.outer(score,score)
    # Arellano/Rogers one-way cluster-robust CR1, G/(G-1)*(N-1)/(N-K).
    vcov=(g/(g-1))*((n-1)/(n-k))*(inv@meat@inv)
    se=np.sqrt(np.maximum(np.diag(vcov),0.0))
    assert np.isfinite(se[:4]).all() and (se[1:4]>0).all()
    p=2*student_t.sf(np.abs(beta[:4]/se[:4]),df=g-1)
    assert np.isfinite(p).all()
    denom=np.sum((target-target.mean())**2)
    r2=1-float((e@e)/denom) if denom>0 else None
    out={}
    for i,key in enumerate(("intercept",*REGRESSORS)):
        out[key+"_coefficient"]=float(beta[i])
        out[key+"_cluster_se"]=float(se[i])
        out[key+"_cluster_t_p"]=float(p[i])
    return {"n":n,"countries":g,"years":len(years),"design_columns":k,
            "country_cluster_df":g-1,"r_squared_with_fixed_effects":r2,
            **out}

def main():
    d=load()
    result=[]
    for horizon in (2021,2024):
      for inv in ("investment_disclosed","investment_estimated"):
       for y in YCOLS:
        for exclude_china in (False,True):
          rows=[r for r in d if r["Year"]<=horizon and
                (not exclude_china or r["ISO3"]!="CHN")]
          n_exp=(horizon-2015)*(29 if exclude_china else 30)
          assert len(rows)==n_exp
          flags={
            "patent_incomplete_rows":sum(not r["patents_complete"] for r in rows),
            "investment_incomplete_rows":sum(not r[inv+"_complete"] for r in rows)
          }
          if horizon==2021:
              assert flags["patent_incomplete_rows"]==0 and flags["investment_incomplete_rows"]==0,flags
          else:
              assert flags["patent_incomplete_rows"]==3*(29 if exclude_china else 30),flags
          stats=fit(rows,y,inv)
          result.append({
            "source_snapshot":SNAPSHOT,"source_zip_sha256":OFFICIAL_ARCHIVE_SHA256,
            "outcome":y,"investment_metric":inv,"end_year":horizon,
            "exclude_CHN":exclude_china,
            "identification":"EXPLORATORY_TWO_WAY_FIXED_EFFECTS_NONCAUSAL",
            "outcome_source":"USER_WORKBOOK_WDI_CLAIM_NOT_ROW_LEVEL_INDEPENDENTLY_VERIFIED",
            "official_CAT_predictors":"VERIFIED_PINNED_ZENODO_V1.12.0",
            "patent_incomplete_included":flags["patent_incomplete_rows"]>0,
            **flags,**stats})
    assert len(result)==16
    assert len({(r["outcome"],r["investment_metric"],r["end_year"],r["exclude_CHN"]) for r in result})==16
    assert all(r["identification"].endswith("NONCAUSAL") for r in result)
    OUT_CSV.parent.mkdir(exist_ok=True,parents=True)
    with OUT_CSV.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
    structured={
        "status":"SOURCE_ATTRIBUTED_OFFICIAL_CAT_PREDICTOR_SENSITIVITY_EXECUTED",
        "n_models":16,
        "source_ETO_CAT_ZENODO_record":22772306,
        "source_ETO_CAT_version":"1.12.0",
        "official_zip_sha256":OFFICIAL_ARCHIVE_SHA256,
        "source_workbook_sha256":hashlib.sha256(PANEL.read_bytes()).hexdigest(),
        "independent_workbook_WDI_retrieval":False,
        "end_year_2021":"ALL_OFFICIAL_PATENT_OBSERVATIONS_COMPLETE",
        "end_year_2024":"INCLUDES_INCOMPLETE_OFFICIAL_PATENTS_2022_2024_FLAGGED_SENSITIVITY",
        "outcomes":"original workbook supplied WDI-proxy outcomes, not independently audited to WDI release",
        "estimand":"Two-way country and year FE OLS, cluster-robust (CR1) by country, t df=G-1",
        "limitations":"Descriptive within-country associations; identification/endogeneity unresolved; multiplicity; 29-30 country clusters; no causal validity; not comparable to Stata GMM",
        "replaces_original_data":False,
        "replaces_original_8_licensed_stata_fits":False,
        "causal_models_approved":0,
        "results":result,
    }
    OUT_JSON.write_text(json.dumps(structured,ensure_ascii=False,indent=2),encoding="utf-8")
    print("OFFICIAL_CAT_2026_V112_FE_REAL_MODELS=16")
    print("COMPLETE_OFFICIAL_PATENTS_PRIMARY_THROUGH_2021_AND_FLAGGED_2024_SENSITIVITY")
    print("ORIGINAL_WORKBOOK_SOURCE_LINEAGE_STILL_UNVERIFIED")
    print("CRITICAL: EXPLORATORY_ASSOCIATION_ONLY, CAUSAL_MODELS_APPROVED=0")
if __name__=="__main__": main()
