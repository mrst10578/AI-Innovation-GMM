"""Structural regression gates only; not an executable Stata interpreter."""
from pathlib import Path
import json, re
ROOT = Path(__file__).resolve().parents[2]

def main():
    f = {p.name: p.read_text(encoding="utf-8") for p in (ROOT / "stata").glob("*.do")}
    required = {"RUN_ALL.do", "01_environment_and_data.do", "02_pre_estimation.do",
                "03_hightech_models.do", "04_unemployment_models.do",
                "05_post_estimation_and_export.do", "06_fit_model.do"}
    assert required <= set(f), sorted(required - set(f))
    model, run, env = (f[x] for x in ("06_fit_model.do", "RUN_ALL.do", "01_environment_and_data.do"))
    assert not re.search(r"(?im)^\s*scalar\s+_n\s*=", model), "reserved Stata name _n"
    assert "AI_GMM_FIX_ID=V3_3301_NONMATA_FIRST" in run
    assert "AI_GMM_FIX_ID=V3_3301_NONMATA_FIRST" in model
    assert model.count("twostep robust small nomata") == 2, "r3301 bypass absent"
    assert model.count("capture noisily xtabond2") == 2
    assert "xtabond2_mata()" in model
    assert 'status "REVIEW_REQUIRED"' in model and 'local status "APPROVED"' not in model
    assert model.count("post __audit") == 2
    assert 'capture scalar sc_invest_b = _b[ln1p_invest]' in model
    assert 'capture scalar sc_patent_b = _b[ln1p_patent]' in model
    assert "HANSEN_REJECTED" in model and "AR2_REJECTED" in model
    assert "NO_DIFFERENCE_HANSEN" in model
    assert "_se[GDP_Growth]" in model
    assert "forvalues attempt" not in model, "Old unverified silent fallback must be removed"
    assert 'str244 flags' in run and 'invest_b invest_se patent_b patent_se' in run
    assert 'foreach outcome in HighTech_Exports Unemployment' in run
    assert 'foreach period in 2024 2023' in run
    assert 'foreach method in difference system' in run
    assert "MODEL_EXECUTION_FAILURES=" in run
    assert 'postclose __audit' in run
    assert 'import excel using "data/raw/AI_Balanced_Panel (1).xlsx", firstrow clear' in env
    assert 'capture confirm file "data/processed/stata_ready.dta"' not in env
    assert 'assert _N == 270' in env and 'isid ISO3 Year' in env
    assert "UPSTREAM_SOURCE_VERSION_NOT_VERIFIED" in env
    assert "xtabond2, version" in env
    for name, script in f.items():
        assert script.count("{") == script.count("}"), name
    print(json.dumps({"status":"STATIC_PASS", "stata_executed":False,
                     "specs":8, "engine":"nomata", "input":"original_xlsx_reimport",
                     "warning":"No Stata runtime or causal-validation claim"}))

if __name__ == "__main__":
    main()
