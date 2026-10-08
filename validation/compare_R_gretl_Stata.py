"""Compare only real output logs. Never infer a Stata result or claim whole-model equivalence."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
MAP={"GRETL_GMM_2024_HIGH_TECH_DIFFERENCE":"HighTech_Exports_2024_d_lag2:3",
"GRETL_GMM_2024_UNEMPLOYMENT_DIFFERENCE":"Unemployment_2024_d_lag2:3"}
VAL=r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"

def r_coeff(text):
    out={}
    for line in text.splitlines():
        if line.startswith("GMM_COEFFICIENTS "):
            bits=line.split(" ",2)
            if len(bits)<3:continue
            key=bits[1]
            for var in ("ln1p_invest","ln1p_patent"):
                match=re.search(re.escape(var)+r"="+VAL,bits[2])
                if match:out.setdefault(key,{})[var]=float(match.group(1))
    return out

def gretl_coeff(text):
    out={};key=None
    for line in text.splitlines():
        line=line.strip()
        if line in MAP:
            key=MAP[line];out[key]={};continue
        if line.startswith("GRETL_GMM_"):key=None
        if key and line:
            for var in ("ln1p_invest","ln1p_patent"):
                m=re.match(re.escape(var)+r"\s+"+VAL,line)
                if m:out[key][var]=float(m.group(1))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--r-log",default="outputs/r_models_log.txt")
    ap.add_argument("--gretl-log",default="outputs/gretl_models_log.txt")
    ap.add_argument("--stata-log",default="outputs/stata_hightech_models.log")
    ap.add_argument("--out",default="outputs/cross_engine_comparison.json")
    a=ap.parse_args()
    paths={k:Path(p) for k,p in [("R",a.r_log),("gretl",a.gretl_log),("Stata",a.stata_log)]}
    missing={k:str(v) for k,v in paths.items() if not v.exists()}
    models_r=r_coeff(paths["R"].read_text(errors="replace")) if paths["R"].exists() else {}
    models_g=gretl_coeff(paths["gretl"].read_text(errors="replace")) if paths["gretl"].exists() else {}
    results={}
    for key in MAP.values():
        rc=models_r.get(key);gc=models_g.get(key)
        if not rc or not gc:
            results[key]={"status":"not_comparable_missing_real_coefficients",
                          "R":rc,"gretl":gc};continue
        delta={v:round(rc[v]-gc[v],8) for v in rc.keys()&gc.keys()}
        results[key]={"status":"coefficients_reproduced_not_tests_certified"
                      if all(abs(val)<1e-4 for val in delta.values()) else "coefficients_disagree",
                      "difference_R_minus_gretl":delta,"R":rc,"gretl":gc,
                      "caveat":"Coefficient agreement does not certify same GMM instrument matrix, SE, Hansen or Sargan weights."}
    result={"research":"AI-Innovation-GMM only",
            "engine_logs_missing":missing,"comparisons":results,
            "Stata_status":"real_log_present_needs_manual_xtabond2_extraction" if paths["Stata"].exists() else "not_run_or_log_unavailable",
            "warnings":["Only 2024 lag2:3 Difference GMM specifications aligned for coefficient comparisons.",
                        "Model validity and overidentification test equivalence require separate moment/weight review."]}
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
