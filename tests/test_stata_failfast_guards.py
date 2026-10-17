"""Offline source-code QA for fail-closed Stata professor-data workflow.

These tests inspect the *current do-files*. Actual execution must separately
be proved by the Stata log and a 16-row diagnostic CSV.
"""
from pathlib import Path
from src.python.preflight import ROOT
D=ROOT/"stata"

def test_raw_excel_is_always_reimported_not_cached():
    code=(D/"01_environment_and_data.do").read_text(encoding="utf-8")
    assert 'import excel using "data/raw/AI_Balanced_Panel (1).xlsx"' in code
    assert 'confirm file "data/raw/AI_Balanced_Panel (1).xlsx"' in code
    assert "Neither processed DTA nor original Excel" not in code
    assert 'use "data/processed/stata_ready.dta"' not in code
    assert "isid ISO3 Year" in code
    assert "assert _N == 270" in code
    assert "assert r(N) == 30" in code

def test_mandatory_tests_are_not_silently_skipped():
    code=(D/"02_pre_estimation.do").read_text(encoding="utf-8")
    assert "MANDATORY_IPS_FAILED" in code and "MANDATORY_FISHER_ADF_FAILED" in code
    assert "if `mandatory_pretest_failed'" in code
    run=(D/"RUN_ALL.do").read_text(encoding="utf-8")
    assert "FATAL_PRE_ESTIMATION_DIAGNOSTICS_FAILED" in run
    assert "STATA_REQUIRED_PRETESTS_COMPLETE=1" in run
    assert "FATAL_INCOMPLETE_GMM_BATCH" in run

def test_all_16_baseline_estimates_required():
    model=(D/"_run_one_model.do").read_text(encoding="utf-8")
    assert "if `successful_gmm' != 8" in model
    assert "INCOMPLETE_GMM_OUTCOME_BUNDLE" in model
    final=(D/"05_post_estimation_and_export.do").read_text(encoding="utf-8")
    assert "FATAL_INCOMPLETE_DIAGNOSTIC_CSV" in final
    assert "if `record_count' != 16" in final
    tablet=(D/"TABLET_RUN.do").read_text(encoding="utf-8")
    assert "AI_STATA_REAL_EXECUTION_RETURN_CODE=" in tablet
    assert "if `result_rc' exit `result_rc'" in tablet

def test_report_contains_all_requested_statistics_and_professor_data_provenance():
    generator=(ROOT/"src/python/build_professor_manuscript.py").read_text(encoding="utf-8")
    for item in ['"Sargan p"','"Hansen p"','"AR(1) p"','"AR(2) p"','"مشاهده"',
                 "توسط استاد ارائه","SE "]:
        assert item in generator

def test_sensitivity_batches_reject_partial_completion():
    stress=(D/"08_instrument_stress.do").read_text(encoding="utf-8")
    assert "STRICT_STRESS_GMM_INCOMPLETE" in stress
    assert "if `fit_count' != 16 | `failed_count' != 0" in stress
    influence=(D/"09_influence_china_usa.do").read_text(encoding="utf-8")
    assert "STRICT_COUNTRY_INFLUENCE_INCOMPLETE" in influence
    assert "if `successes' != 12 | `fails' != 0" in influence

def test_reference_model_analysis_is_not_mislabeled_causal():
    source=(ROOT/"docs/PROFESSOR_SUPPLIED_DATA_POLICY_FA.md").read_text(encoding="utf-8")
    rationale=(ROOT/"docs/REFERENCE_MODEL_RATIONALE_FA.md").read_text(encoding="utf-8")
    assert "داده" in source and "استاد" in source
    assert "hi_2024_S23_E" in rationale and "un_2024_S23_E" in rationale
    assert "شناسایی" in rationale and "علّی" in rationale
