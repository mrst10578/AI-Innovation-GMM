"""Independently attest a *completed real Stata* strict baseline rerun on tablet.

Usage:
  python src/python/verify_stata_strict_rerun.py /storage/emulated/0/Download/AI_Innovation_Stata_Ready
Requires only Python standard library; does not fit any model.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from datetime import datetime,timezone
from pathlib import Path

SOURCE_SHA="4f9bf76658d1f495d3eb3e39b226bb5ba6ac39446b35e41bfce4a2aab65d0434"
EXPECTED_MODELS=16

def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""): h.update(block)
    return h.hexdigest()

def attest(root:Path)->dict:
    root=root.expanduser()
    d=root/"outputs/stata"
    source=root/"data/raw/AI_Balanced_Panel (1).xlsx"
    required=[source,d/"00_master.log",d/"hightech.log",d/"unemployment.log",
              d/"TABLET_FINISH_STATUS.log",d/"gmm_diagnostics.csv"]
    for p in required:
        if not p.is_file() or p.stat().st_size==0:raise RuntimeError("Required Stata input/output missing: "+str(p))
    if sha256(source)!=SOURCE_SHA: raise RuntimeError("Professor original Excel SHA mismatch")
    logs={k:(d/k).read_text(encoding="utf-8",errors="replace")
          for k in ("00_master.log","hightech.log","unemployment.log","TABLET_FINISH_STATUS.log")}
    master=logs["00_master.log"]
    status=logs["TABLET_FINISH_STATUS.log"]
    flags=[
        ("original Excel reimported", "ORIGINAL_INSTRUCTOR_EXCEL_REIMPORTED_AND_VALIDATED=1" in master),
        ("all mandatory pretests completed","STATA_REQUIRED_PRETESTS_COMPLETE=1" in master),
        ("all 16 baseline fits completed","STATA_GMM_ALL_16_COMPLETE=1" in master),
        ("both outcomes have eight fits",logs["hightech.log"].count("GMM_SUCCESSFUL_FITS=8")==1 and logs["unemployment.log"].count("GMM_SUCCESSFUL_FITS=8")==1),
        ("postestimation produced 16 status records","STATA_DIAGNOSTIC_RECORDS=16 FAILED=0" in master),
        ("tablet process returned zero",bool(re.search(r"^AI_STATA_REAL_EXECUTION_RETURN_CODE=0\s*$",status,re.M))),
        ("no fatal runtime marker",not re.search(r"^(?:FATAL_|MANDATORY_IPS_FAILED|MANDATORY_FISHER_ADF_FAILED|MODEL_FAILED)",master,re.M)),
    ]
    bad=[label for label,pass_ in flags if not pass_]
    if bad:raise RuntimeError("Required actual Stata completion markers missing: "+", ".join(bad))
    with (d/"gmm_diagnostics.csv").open(newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=EXPECTED_MODELS or len({r["model"] for r in rows})!=EXPECTED_MODELS:
        raise RuntimeError("Expected exactly 16 unique baseline model diagnostics")
    if any(int(r["rc"])!=0 for r in rows):raise RuntimeError("A required Stata model failed")
    estimates=[d/(r["model"]+".ster") for r in rows]
    absent=[p.name for p in estimates if not p.is_file() or p.stat().st_size==0]
    if absent:raise RuntimeError("Missing genuine Stata .ster estimates: "+", ".join(absent))
    now= (d/"TABLET_FINISH_STATUS.log").stat().st_mtime
    if any(abs(now-p.stat().st_mtime)>3600 for p in estimates+[d/"gmm_diagnostics.csv"]):
        raise RuntimeError("At least one .ster or diagnostics file is stale (>1 hour older than finish receipt)")
    if any(abs(now-p.stat().st_mtime)>3600 for p in (d/"00_master.log",d/"hightech.log",d/"unemployment.log")):
        raise RuntimeError("At least one Stata log is stale (>1 hour older than finish receipt)")
    result={
        "status":"STRICT_STATA_BASELINE_RERUN_VERIFIED",
        "verified_at_utc":datetime.now(timezone.utc).isoformat(),
        "actual_finish_modified_at_utc":datetime.fromtimestamp(now,timezone.utc).isoformat(),
        "research_source":"instructor-supplied Bahar workbook, 30 countries, 2016-2024",
        "source_sha256":SOURCE_SHA,
        "mandatory_pretests_complete":True,
        "baseline_gmm_estimates":16,
        "baseline_gmm_failed":0,
        "real_stata_ester_files":len(estimates),
        "exit_code":0,
        "checklist":{name:status for name,status in flags},
        "output_evidence_sha256":{p.name:sha256(p) for p in required if p!=source},
        "model_instruments_and_diagnostic_status":[{
            "model":r["model"],"status":r["status"],"N":int(r["N"]),
            "groups":int(r["Ng"]),"instruments":int(r["instruments"])
        } for r in rows],
        "scientific_limit":"Software completion does not establish causal identification or validity of GMM level moment restrictions."
    }
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    att=attest(args.root)
    content=json.dumps(att,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(content,encoding="utf-8")
    print(content)
