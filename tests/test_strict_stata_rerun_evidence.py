"""Ensure strict, actually completed licensed Stata rerun evidence is archived.

The raw device-file SHA256 fields refer to CRLF/Winlator source files. Text logs
stored in GitHub can normalize line endings, so do not compare these raw hashes
to a line-ending-normalized Git blob.
"""
import csv
import json
import re
from src.python.preflight import ROOT

def test_strict_live_rerun_attestation_is_consistent():
    p=ROOT/"reports"
    receipt=json.loads((p/"STRICT_STATA_RERUN_RECEIPT_20261017.json").read_text(encoding="utf-8"))
    assert receipt["status"]=="STRICT_STATA_BASELINE_RERUN_VERIFIED"
    assert receipt["exit_code"]==0
    assert receipt["baseline_gmm_estimates"]==16
    assert receipt["baseline_gmm_failed"]==0
    assert receipt["real_stata_ester_files"]==16
    assert receipt["mandatory_pretests_complete"] is True
    assert all(receipt["checklist"].values())
    models=receipt["model_instruments_and_diagnostic_status"]
    with (p/"STATA_REAL_gmm_diagnostics_20261017.csv").open(encoding="utf-8",newline="") as f:
        expected=list(csv.DictReader(f))
    assert len(models)==len(expected)==16
    for a,b in zip(models,expected):
        assert (a["model"],a["status"],a["N"],a["groups"],a["instruments"])==(
            b["model"],b["status"],int(b["N"]),int(b["Ng"]),int(b["instruments"]))
    finish=(p/"STATA_STRICT_TABLET_FINISH_20261017.log").read_text(encoding="utf-8")
    assert "AI_STATA_REAL_EXECUTION_RETURN_CODE=0" in finish
    assert "AI_STATA_ALL_BASELINE_EXECUTED" in finish

def test_full_strict_master_and_outcome_evidence_is_not_partial():
    p=ROOT/"reports"
    master=(p/"STATA_STRICT_master_20261017.log").read_text(encoding="utf-8")
    hi=(p/"STATA_STRICT_hightech_20261017.log").read_text(encoding="utf-8")
    un=(p/"STATA_STRICT_unemployment_20261017.log").read_text(encoding="utf-8")
    assert "ORIGINAL_INSTRUCTOR_EXCEL_REIMPORTED_AND_VALIDATED=1" in master
    assert "STATA_REQUIRED_PRETESTS_COMPLETE=1" in master
    assert "STATA_DIAGNOSTIC_RECORDS=16 FAILED=0" in master
    assert "STATA_GMM_ALL_16_COMPLETE=1" in master
    assert master.count("GMM_SUCCESSFUL_FITS=8")==2
    assert "GMM_SUCCESSFUL_FITS=8" in hi and "GMM_SUCCESSFUL_FITS=8" in un
    assert len(master.splitlines())==3454
    assert len(hi.splitlines())==1317 and len(un.splitlines())==1317
    assert re.search(r"^(?:FATAL_|MODEL_FAILED|MANDATORY_IPS_FAILED|MANDATORY_FISHER_ADF_FAILED)",master,re.M) is None
