"""Emit professor-requested pre/post estimation tables from ACTUAL archived Stata logs.
No re-estimation, no imported datasets or synthesized p-values.
Usage: python -m src.python.professor_diagnostics_tables
"""
from __future__ import annotations
import csv
import re
from pathlib import Path
from src.python.preflight import ROOT

R=ROOT/"reports"
def save(name, rows, cols):
    path=R/name
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print("SAVED",path,len(rows))

def source_rows(name):
    with (R/name).open(encoding="utf-8",newline="") as f: return list(csv.DictReader(f))

def pre_estimations():
    s=(R/"STATA_REAL_master_20261017.log").read_text(encoding="utf-8")
    t=re.split(r"IPS unit root test, intercept, 1 ADF lag: (HighTech_Exports|Unemployment|ln_ai_investment|ln_ai_patents|GDP_Growth)\n",s)
    result=[]
    for i in range(1,len(t)-1,2):
        var,portion=t[i],t[i+1]
        a=re.search(r"W-t-bar\s+([-+.\d]+)\s+([-+.\d]+)",portion)
        b=re.search(r"Inverse chi-squared\(60\)\s+P\s+([-+.\d]+)\s+([-+.\d]+)",portion)
        if a is None or b is None: raise RuntimeError(f"Missing actual unit-root statistics: {var}")
        result.append({
            "variable":var,"N_groups":"30","T_years":"9","lag":"1",
            "IPS_W_t_bar":a.group(1),"IPS_p":a.group(2),
            "Fisher_ADF_P":b.group(1),"Fisher_ADF_P_p":b.group(2),
            "first_generation_caveat":"short T; cross-sectional dependence may violate assumptions",
            "source":"STATA_REAL_master_20261017.log"
        })
    if len(result)!=5:raise RuntimeError(f"Expected 5 paired IPS/Fisher outputs, got {len(result)}")
    save("PROFESSOR_PRE_ESTIMATION_20261017.csv",result,list(result[0]))
    if s.count("estat vif")<2 or "pwcorr HighTech_Exports" not in s:
        raise RuntimeError("VIF/correlation source not found")
    return result

def model_diagnostics():
    stress_log=(R/"STATA_REAL_instrument_stress_v2_20261017.log").read_text(encoding="utf-8")
    rows=source_rows("STATA_REAL_stress_v2_20261017.csv")
    joint={r["model"]:r for r in source_rows("STATA_REAL_joint_hypotheses_20261017.csv")}
    out=[]
    for r in rows:
        tag=r["model"]
        found=re.search(r"^STRESS_ATTEMPT="+re.escape(tag)+r"\b.*$",stress_log,re.M)
        if not found: raise RuntimeError(f"Missing model label in original log: {tag}")
        tail=stress_log[found.end():]
        next_start=re.search(r"^STRESS_ATTEMPT=(?:hi|un)_20\d{2}_(?:D23|S23)_[XE]",tail,re.M)
        if next_start:tail=tail[:next_start.start()]
        level_df=""
        level_excluded_p=""
        level_difference_p=""
        if "_S23_" in tag:
            match=re.search(
                r"Difference-in-Hansen tests of exogeneity of instrument subsets:\s+"
                r"GMM instruments for levels\s+"
                r"Hansen test excluding group:\s+chi2\((\d+)\)\s*=\s*([\d.]+)\s+Prob > chi2 =\s*([\d.]+)\s+"
                r"Difference \(null H = exogenous\):\s+chi2\((\d+)\)\s*=\s*([\d.]+)\s+Prob > chi2 =\s*([\d.]+)",tail)
            if match is None:raise RuntimeError(f"Missing genuine subset test: {tag}")
            level_df,level_excluded_p,level_difference_p=match.group(1),match.group(3),match.group(6)
        j=joint[tag]
        ins=int(float(r["instruments"]))
        ng=int(float(r["Ng"]))
        ap=float(r["ar1_p"])
        a2=float(r["ar2_p"])
        hp=float(r["hansen_p"])
        out.append({
            "model":tag,"outcome":"HighTech_Exports" if tag.startswith("hi_") else "Unemployment",
            "sample_end":"2024" if "_2024_" in tag else "2023",
            "GMM_type":"system" if "_S23_" in tag else "difference",
            "GDP_assumption":"endogenous_lags2to3" if tag.endswith("_E") else "strictly_exogenous_provisional",
            "groups":ng,"instrument_count":ins,"instruments_lt_groups":ins<ng,
            "AR1_p":r["ar1_p"],"AR1_expected_lt_0_05":ap<.05,
            "AR2_p":r["ar2_p"],"AR2_no_rejection_p_gt_0_05":a2>.05,
            "Hansen_robust_p":r["hansen_p"],"Hansen_midrange_0_05_to_0_95":.05<hp<.95,
            "Sargan_nonrobust_p":r["sargan_p"],
            "level_exclusion_hansen_df":level_df,
            "level_exclusion_hansen_p":level_excluded_p,
            "level_instrument_diff_Hansen_p":level_difference_p,
            "joint_AI_Wald_p":j["joint_ai_p"],
            "lagged_y_equals_1_Wald_p":j["persistence_equal1_p"],
            "singular_moment_covariance_warning":"no (in this specific 16-fit log)",
            "scientific_certification":"UNVALIDATED",
            "primary_log":"STATA_REAL_instrument_stress_v2_20261017.log"
        })
    if len(out)!=16:raise RuntimeError("Expected 16 second-round results")
    if sum(bool(r["level_exclusion_hansen_df"]) for r in out)!=8:raise RuntimeError("Expected 8 system-GMM subset tests")
    save("PROFESSOR_POST_ESTIMATION_20261017.csv",out,list(out[0]))
    return out

if __name__=="__main__":
    pre_estimations()
    model_diagnostics()
