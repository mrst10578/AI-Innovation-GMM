"""Validate actual R sensitivity CSV, preserving non-estimation and diagnostics.
All 32 rows correspond to REAL attempted estimation, not synthetic numbers.
"""
import csv,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/"outputs/r_china_instrument_sensitivity.csv"
if not p.exists():raise SystemExit("R sensitivity run absent; DO NOT simulate")
with p.open(encoding="utf-8",newline="") as h:rows=list(csv.DictReader(h))
expected={(y,str(yr),method,str(lag),str(ex).upper())
          for y in ("HighTech_Exports","Unemployment") for yr in (2023,2024)
          for method in ("difference","system") for lag in (2,3)
          for ex in ("FALSE","TRUE")}
seen=[(v["outcome"],v["end_year"],v["method"],v["instrument_lag_end"],v["exclude_CHN"].upper()) for v in rows]
assert len(rows)==32 and len(set(seen))==32 and set(seen)==expected,(len(rows),set(seen)^expected)
issues=[];pairs=[];nonerror=[v for v in rows if v["status"]!="ERROR"]
for v in rows:
 expected_countries=29 if v["exclude_CHN"].upper()=="TRUE" else 30
 if int(v["countries"])!=expected_countries:issues.append(("WRONG_COUNTRY_COUNT",v["spec"]))
 if v["status"]=="ERROR":issues.append(("RUN_ERROR",v["spec"],v["failure_detail"]))
 if v["status"].startswith("AR2_REJECTED"):issues.append(("AR2_REJECTED",v["spec"]))
 if "OVERID_REJECTED" in v["status"]:issues.append(("OVERID_REJECTED",v["spec"]))
 if "NOT_TESTABLE" in v["status"]:issues.append(("NOT_TESTABLE",v["spec"]))
 if "TOO_MANY" in v["status"]:issues.append(("TOO_MANY_INSTRUMENTS",v["spec"]))
def val(x):
 try:
  f=float(x);return f if math.isfinite(f) else None
 except (ValueError,TypeError):return None
by={(v["outcome"],v["end_year"],v["method"],v["instrument_lag_end"],v["exclude_CHN"].upper()):v for v in rows}
for y in ("HighTech_Exports","Unemployment"):
 for yr in ("2023","2024"):
  for kind in ("difference","system"):
   for lag in ("2","3"):
    a=by[(y,yr,kind,lag,"FALSE")];b=by[(y,yr,kind,lag,"TRUE")]
    z={"outcome":y,"year":yr,"method":kind,"instrument_lag_end":lag}
    for coef in ("invest_b","patent_b"):
     u,v=val(a[coef]),val(b[coef])
     z[coef+"_full"]=u;z[coef+"_exclude_CHN"]=v
     z[coef+"_sign_changed"]=(u*v<0 if u is not None and v is not None else None)
    pairs.append(z)
assert nonerror,"All 32 real R estimates failed; investigation required"
out={"type":"REAL R ONE-STEP pgmm country/instrument sensitivity, NOT Stata replication",
     "scenarios":32,"estimated":len(nonerror),"runtime_errors":32-len(nonerror),
     "diagnostic_flags":issues,"china_exclusion_pairs":pairs,
     "all_models_causally_approved":False,
     "prohibited_interpretation":"Do not select results based on significance; no official CAT row-level provenance."}
(root/"outputs/r_china_instrument_sensitivity_qc.json").write_text(json.dumps(out,indent=2,ensure_ascii=False))
print("REAL_R_SENSITIVITY_AUDIT",json.dumps({"scenarios":32,"estimated":len(nonerror),
    "runtime_errors":32-len(nonerror),"flags":len(issues),"pairs":len(pairs)}))
