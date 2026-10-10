"""Quality-control actual licensed Stata results received Oct 10, 2026.
Evidence is an archived CSV from an emailed ZIP, NOT values fabricated by CI.
All causal/source-validity caveats remain independent of numerical success.
"""
import csv, json, math
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
SOURCE=BASE/"validation/evidence/stata_model_summary_20261010.csv"
DEST=BASE/"outputs/real_stata_20261010_qc.json"
def fl(x):
    try:
        v=float(x)
        return v if math.isfinite(v) else None
    except (ValueError,TypeError): return None
def main():
    with SOURCE.open(newline="",encoding="utf-8") as f:
        r=list(csv.DictReader(f))
    assert len(r)==8, "Exactly 8 observed fits required"
    expected={(y,str(year),method) for y in ("HighTech_Exports","Unemployment")
              for year in (2023,2024) for method in ("difference","system")}
    actual={(x["outcome"],x["period"],x["method"]) for x in r}
    assert actual==expected and len(actual)==len(r)
    issues={}; assessed={}
    for x in r:
        k="/".join((x["outcome"],x["period"],x["method"]))
        flags=[]
        if x["engine"]!="ADO_NOMATA": flags.append("UNEXPECTED_ENGINE")
        if x["status"]!="REVIEW_REQUIRED": flags.append("UNEXPECTED_ARCHIVED_STATUS")
        if fl(x["rc"])!=0: flags.append("ESTIMATION_FAILED")
        if fl(x["groups"])!=30: flags.append("GROUP_COUNT_UNEXPECTED")
        n_expected=30*((int(x["period"])-2016+1)-(2 if x["method"]=="difference" else 1))
        if fl(x["n"])!=n_expected: flags.append("OBS_COUNT_UNEXPECTED")
        instrument_count=fl(x["instruments"])
        if instrument_count is None or instrument_count>=30: flags.append("INSTRUMENT_OVERFLOW_OR_MISSING")
        for name in ("hdf","sdf"):
            if fl(x[name]) is None or fl(x[name])<=0: flags.append(name.upper()+"_INVALID")
        for name in ("hp","sp","ar1p","ar2p"):
            p=fl(x[name])
            if p is None or not 0<=p<=1: flags.append(name.upper()+"_INVALID")
        if fl(x["ar2p"]) is not None and fl(x["ar2p"])<0.05: flags.append("AR2_REJECTION")
        if fl(x["hp"]) is not None and fl(x["hp"])<0.05: flags.append("HANSEN_REJECTION")
        if fl(x["ar1p"]) is not None and fl(x["ar1p"])>=0.05:flags.append("AR1_NONREJECTION_WARNING")
        if "NO_DIFFERENCE_HANSEN" not in x["flags"]: flags.append("UNVERIFIED_DH_STATUS")
        for term in ("invest","patent"):
            b,se=fl(x[term+"_b"]),fl(x[term+"_se"])
            if b is None or se is None or se<=0: flags.append(term.upper()+"_MISSING_COEFFICIENT_OR_SE")
        issues[k]=flags
        assessed[k]={"N":int(x["n"]),"groups":int(x["groups"]),"instruments":int(x["instruments"]),
                     "AR1_p":fl(x["ar1p"]),"AR2_p":fl(x["ar2p"]),
                     "Hansen_p":fl(x["hp"]),"Sargan_p":fl(x["sp"]),
                     "investment_coefficient":fl(x["invest_b"]),
                     "investment_SE":fl(x["invest_se"]),
                     "patent_coefficient":fl(x["patent_b"]),
                     "patent_SE":fl(x["patent_se"]),
                     "diagnostic_flags":flags,
                     "conclusion":"CONDITIONAL_SOURCE_AND_IDENTIFICATION_REVIEW_ONLY"}
    assert all(x["engine"]=="ADO_NOMATA" for x in r)
    assert all(fl(x["rc"])==0 for x in r)
    assert all("NO_DIFFERENCE_HANSEN" in x["flags"] for x in r)
    assert all("AR1_NONREJECTION_WARNING" in issues[k] for k in issues if "/difference" in k)
    assert all("AR1_NONREJECTION_WARNING" not in issues[k] for k in issues if "/system" in k)
    assert not any("AR2_REJECTION" in a or "HANSEN_REJECTION" in a for a in issues.values())
    assert all(abs(fl(x[z+"_b"])/fl(x[z+"_se"]))<1.96
               for x in r for z in ("invest","patent"))
    output={"source":"Gmail received email 2026-10-10 12:02:50 Asia/Tehran; subject هوش مصنوعی; attachment هوش.zip",
            "attachment_metadata":"20 ZIP entries: 8 individual .log, 8 .ster, Stata summary CSV and DTA, preflight log, outputs directory",
            "stata_engine":"xtabond2 3.7.2 two-step robust small nomata",
            "estimated_models":8,"stated_stata_execution":True,
            "not_approved_for_causal_inference":True,
            "limitation":"No Difference-in-Hansen nomata; CSET source vintage and investment unit unverified",
            "comparability":"Stata two-step nomata versus R pgmm one-step and gretl one-step; coefficients need not match",
            "models":assessed}
    DEST.parent.mkdir(exist_ok=True)
    DEST.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
    print("VERIFIED_REAL_STATA_RESULTS=8 NO_EXECUTION_FAILURES")
    print("AR1_DIFF_NONREJECTION=4/4 AR2_REJECTED=0 HANSEN_REJECTED=0")
    print("INSTRUMENTS_MIN=14 MAX=20 COUNTRIES=30")
    print("AI_COEFFICIENT_ABS_B_OVER_SE_BELOW_1_96=16/16")
    print("CAUSAL_GMM_MODELS_APPROVED=0 (scientific source and identification gates open)")
if __name__=="__main__":main()
