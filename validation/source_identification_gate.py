"""Evidence-blocking provenance/identification gate (not an estimator).

Checks 2026-10-10 real Stata table without inventing source provenance.
Passing this script means the audit ran and detected unresolved risks, NOT
that the model passed scientific review.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "validation/source_provenance_manifest.json"
STATA = ROOT / "validation/evidence/stata_model_summary_20261010.csv"
DEST = ROOT / "outputs/source_identification_gate.json"

def evaluate(manifest, rows):
    assert manifest["original_workbook_sha256"] == "4f9bf76658d1f495d3eb3e39b226bb5ba6ac39446b35e41bfce4a2aab65d0434"
    assert manifest["research_data"]["rows"] == 270
    assert len(rows) == 8
    expected = {(y, str(t), k) for y in ("HighTech_Exports", "Unemployment")
                for t in (2023, 2024) for k in ("difference", "system")}
    observed = [(r["outcome"], r["period"], r["method"]) for r in rows]
    assert len(set(observed)) == 8 and set(observed) == expected
    assert all(r["engine"] == "ADO_NOMATA" and r["rc"] == "0" for r in rows)
    assert all("NO_DIFFERENCE_HANSEN" in r["flags"] for r in rows)

    # Evidence URLs alone are insufficient: verification requires exact matched data
    # source, indicator definition, version and row-level provenance.
    def checklist(group):
        result = {}
        for key, v in manifest[group].items():
            assert isinstance(v["verified"], bool)
            if v["verified"]:
                assert isinstance(v["evidence_url"], str) and v["evidence_url"].startswith("https://"), (
                    "Verified source claims require a cited evidence URL: " + key)
            result[key] = {"verified": v["verified"], "evidence_url": v["evidence_url"]}
        return result
    source = checklist("source_evidence")
    moments = checklist("system_gmm_identification")
    source_all = all(x["verified"] for x in source.values())
    moments_all = all(x["verified"] for x in moments.values())

    out = {
        "audited_evidence": "Actual licensed Stata xtabond2 3.7.2 nomata output received by email 2026-10-10",
        "original_workbook_hash": manifest["original_workbook_sha256"],
        "actual_stata_models": 8,
        "stata_technically_executed": True,
        "source_reconciliation": "VERIFIED" if source_all else "BLOCKED_MISSING_MATCHED_EXPORT",
        "system_moment_identification": "VERIFIED" if moments_all else "BLOCKED_UNTESTED_LEVEL_RESTRICTIONS",
        "difference_in_hansen_available": False,
        "system_models": 4,
        "difference_models": 4,
        "difference_models_ar1_nonreject_at_5pct": sum(
            r["method"] == "difference" and float(r["ar1p"]) >= .05 for r in rows),
        "investment_and_patent_coefficients_significant_at_5pct_by_abs_b_se": sum(
            abs(float(r[var+"_b"])/float(r[var+"_se"])) >= 1.96
            for r in rows for var in ("invest","patent")),
        "current_causal_conclusion_approved": False,
        "missing_source_fields": sorted(k for k, v in source.items() if not v["verified"]),
        "missing_identification_fields": sorted(k for k, v in moments.items() if not v["verified"]),
        "scope_note": "Current source/moment blockers remain regardless of passing CI; no causal reclassification.",
        "official_dataset_is_only_candidate": True
    }
    assert len(out["missing_source_fields"]) >= 1
    assert len(out["missing_identification_fields"]) >= 1
    assert out["difference_models_ar1_nonreject_at_5pct"] == 4
    assert out["investment_and_patent_coefficients_significant_at_5pct_by_abs_b_se"] == 0
    return out

def main():
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    with STATA.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    out=evaluate(manifest,rows)
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))
    print("AUDIT_COMPLETE_SOURCE_BLOCKED=" + str(out["source_reconciliation"].startswith("BLOCKED")))
    print("AUDIT_COMPLETE_IDENTIFICATION_BLOCKED=" + str(out["system_moment_identification"].startswith("BLOCKED")))

if __name__ == "__main__":
    main()
