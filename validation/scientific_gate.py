"""Scientific quality flags from ACTUAL R and gretl logs; never select by coefficient significance."""
from pathlib import Path
import re,json,math
OUT=Path("outputs")
def pf(x):
    try:
        f=float(x)
        return f if math.isfinite(f) else None
    except (TypeError,ValueError):return None
def inspect_r(txt):
    out={}
    for line in txt.splitlines():
        q=line.split()
        if line.startswith("GMM ") and " groups " in line:
            key=q[1];out[key]={"source":"R plm 2.6.3","sample_period":key.split("_")[1],
                    "method":"System" if "_ld_" in key else "Difference",
                    "observations_printed_by_pgmm":int(q[q.index("n")+1]),
                    "n_note":"System pgmm nobs can count STACKED equations, not raw unique country-years",
                    "groups":int(q[q.index("groups")+1]),
                    "instrument_columns":int(q[-1]),
                    "ar1":None,"ar2":None,"overid_df":None,"overid_p":None}
        elif line.startswith("OVERID ") and " twosteps " in line:
            k=q[1]
            if k in out:
                out[k]["overid_p"]=pf(q[4]);out[k]["overid_df"]=pf(q[-1])
        elif line.startswith("OVERID_INVALID ") and " twosteps " in line:
            if q[1] in out:out[q[1]]["overid_status"]="ZERO_DF_OR_INVALID"
        elif line.startswith("AB_SERIAL "):
            k=q[1];degree=q[3]
            if k in out and degree in ("1","2"):
                out[k]["ar"+degree]=pf(q[-1])
    for k,v in out.items():
        issues=[]
        if v["instrument_columns"]>=v["groups"]:issues.append("INSTRUMENTS_AT_LEAST_GROUPS")
        if v["ar2"] is None:issues.append("AR2_UNAVAILABLE")
        elif v["ar2"]<.05:issues.append("AR2_REJECTS")
        if v.get("overid_status")=="ZERO_DF_OR_INVALID" or v["overid_df"] is None or v["overid_df"]<=0:issues.append("OVERID_UNTESTABLE")
        elif v["overid_p"] is None:issues.append("OVERID_NAN")
        elif v["overid_p"]<.05:issues.append("OVERID_REJECTS_FOR_REPORTED_WEIGHT")
        if v["ar1"] is None:issues.append("AR1_NAN")
        elif v["ar1"]>=.05:issues.append("AR1_NONREJECTION_WARNING")
        v["diagnostics"]=issues
        v["decision"]="NOT_APPROVED" if any(i in issues for i in
             ("AR2_UNAVAILABLE","AR2_REJECTS","OVERID_UNTESTABLE","OVERID_NAN",
              "OVERID_REJECTS_FOR_REPORTED_WEIGHT","INSTRUMENTS_AT_LEAST_GROUPS")) else "CONDITIONAL_ONLY"
        v["warning"]="Sargan weights are NOT automatic robust Hansen; CSET source vintage and unit remain unverified"
    return out
def inspect_gretl(txt):
    out={};key=None
    for line in txt.splitlines():
        s=line.strip()
        if s.startswith("GRETL_GMM_"):
            key=s;out[key]={"source":"gretl 2023c", "ar1":None,"ar2":None,
                            "sargan_nonrobust_p":None,"instrument_columns":None}
        if key and s.startswith("Number of instruments ="):
            out[key]["instrument_columns"]=int(s.split("=")[-1].strip())
        if key and s.startswith("Test for AR("):
            match=re.search(r"AR\((1|2)\).*?\[([0-9.]+)\]",s)
            if match:out[key]["ar"+match.group(1)]=pf(match.group(2))
        if key and s.startswith("Sargan over-identification test:"):
            match=re.search(r"\[([0-9.]+)\]",s)
            if match:out[key]["sargan_nonrobust_p"]=pf(match.group(1))
    for key,v in out.items():
        issues=[]
        if v["instrument_columns"] is None:issues.append("INSTRUMENTS_MISSING")
        elif v["instrument_columns"]>=30:issues.append("INSTRUMENTS_AT_LEAST_30")
        if v["ar2"] is None:issues.append("AR2_MISSING")
        elif v["ar2"]<.05:issues.append("AR2_REJECTS")
        if v["sargan_nonrobust_p"] is None:issues.append("SARGAN_MISSING")
        elif v["sargan_nonrobust_p"]<.05:issues.append("NONROBUST_SARGAN_REJECTS")
        if v["ar1"] is None or v["ar1"]>=.05:issues.append("AR1_NONREJECTION_OR_MISSING")
        v["issues"]=issues
        v["decision"]="NOT_APPROVED" if any(i in issues for i in
           ("INSTRUMENTS_MISSING","INSTRUMENTS_AT_LEAST_30","AR2_MISSING",
            "AR2_REJECTS","SARGAN_MISSING","NONROBUST_SARGAN_REJECTS")) else "CONDITIONAL_ONLY"
        v["warning"]="Only nonrobust Sargan shown. No verified robust Hansen or Difference-in-Hansen."
    return out
def main():
    p=OUT/"r_models_log.txt";q=OUT/"gretl_models_log.txt"
    assert p.is_file() and q.is_file(),"Real R and gretl logs required, no inferred tests"
    r=inspect_r(p.read_text(errors="replace"))
    g=inspect_gretl(q.read_text(errors="replace"))
    assert len(r)==16,len(r)
    assert len(g)==6,len(g)
    # Every model must be accounted for, including those that failed scientific gates.
    decisions={"study":"AI only","R":r,"gretl":g,
       "stata":"NOT EXECUTED","source_verification":"UNRESOLVED",
       "disclaimer":"These gates classify diagnostic warning signs, not proof of valid instruments.",
       "unit_root_note":"IPS/Fisher with T=9 are low-power; high-tech exports nonrejection is not proof of stationarity."}
    (OUT/"scientific_gate.json").write_text(json.dumps(decisions,ensure_ascii=False,indent=2))
    print("SCIENCE_GATE_R",len(r),"NOT_APPROVED",sum(x["decision"]=="NOT_APPROVED" for x in r.values()))
    print("SCIENCE_GATE_GRETL",len(g),"NOT_APPROVED",sum(x["decision"]=="NOT_APPROVED" for x in g.values()))
    for k,v in r.items():print("R_GATE",k,v["decision"],",".join(v["diagnostics"]) or "CONDITIONAL_SOURCE")
    for k,v in g.items():print("GRETL_GATE",k,v["decision"],",".join(v["issues"]) or "CONDITIONAL_SOURCE")
if __name__=="__main__":main()
