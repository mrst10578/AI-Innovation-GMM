"""Offline test: validates archived live WDI comparison without fresh data access."""
import csv
import json
from pathlib import Path
from src.python.preflight import ROOT

def test_archived_wdi_reference_traceability():
    report=json.loads((ROOT/"reports/WDI_REFERENCE_RECONCILIATION_20261017.json").read_text(encoding="utf-8"))
    assert report["original_sha256"]=="4f9bf76658d1f495d3eb3e39b226bb5ba6ac39446b35e41bfce4a2aab65d0434"
    assert report["original_rows"]==270
    ref=report["source_results"]
    assert {k:(int(v["matches_within_0.001"]),int(v["differences_above_0.001"]),int(v["missing_reference_observations"])) for k,v in ref.items()}=={
        "HighTech_Exports":(253,17,0),
        "GDP_Growth":(270,0,0),
        "Unemployment":(270,0,0)
    }
    assert all(v["reference_lastupdated"]=="2026-10-08" for v in ref.values())
    with (ROOT/"reports/WDI_REFERENCE_ROW_COMPARISON_20261017.csv").open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==810
    assert len(set((r["source_col"],r["ISO3"],r["Year"]) for r in rows))==810
    a=[r for r in rows if r["source_col"]=="HighTech_Exports" and r["equal_to_0.001"]=="False"]
    assert len(a)==17
    maxdif=max(a,key=lambda r:float(r["absolute_deviation"]))
    assert (maxdif["ISO3"],maxdif["Year"])==("FRA","2020")
    assert abs(float(maxdif["absolute_deviation"])-1.34820143802)<1e-8

def test_early_email_not_necessarily_latest_wdi_release():
    report=json.loads((ROOT/"reports/WDI_REFERENCE_RECONCILIATION_20261017.json").read_text(encoding="utf-8"))
    assert report["email_received"]=="2026-09-30"
    assert report["source_results"]["HighTech_Exports"]["reference_lastupdated"]>"2026-09-30"
    # Updating the API does not warrant changing the supplied dataset or asserting a source error.
    import hashlib
    path=ROOT/"data/raw/AI_Balanced_Panel (1).xlsx"
    assert hashlib.sha256(path.read_bytes()).hexdigest()==report["original_sha256"]
