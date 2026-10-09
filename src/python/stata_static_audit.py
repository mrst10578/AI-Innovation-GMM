"""Static consistency checks only: cannot parse or execute real Stata."""
from pathlib import Path
import json
import re
ROOT=Path(__file__).resolve().parents[2]
def main():
    f={p.name:p.read_text() for p in (ROOT/"stata").glob("*.do")}
    assert {"RUN_ALL.do","01_environment_and_data.do","02_pre_estimation.do",
            "03_hightech_models.do","04_unemployment_models.do","05_post_estimation_and_export.do",
            "06_fit_model.do"}<=set(f)
    assert 'postfile __audit' in f["RUN_ALL.do"] and 'postclose __audit' in f["RUN_ALL.do"]
    assert 'capture noisily do "stata/04_unemployment_models.do"' in f["RUN_ALL.do"]
    assert 'ssc install xtabond2' in f["01_environment_and_data.do"]
    assert 'assert _N == 270' in f["01_environment_and_data.do"]
    assert 'isid ISO3 Year' in f["01_environment_and_data.do"]
    for name in ("03_hightech_models.do","04_unemployment_models.do"):
        for year in ("2023","2024"):
            for mode in ("difference","system"):
                assert year+" "+mode in f[name],(name,year,mode)
    model=f["06_fit_model.do"]
    for token in ("noleveleq","twostep robust small","lag(2 3) collapse",
                  "lag(1 2) collapse","split","e(hansen_df)","e(hansenp)",
                  "e(sarganp)","e(ar2p)","e(j)","e(N_g)","post __audit"):
        assert token in model,token
    # Regression guards for real-world Stata r(198) and silent model omissions.
    assert not re.search(r"(?im)^\s*scalar\s+_n\s*=", model), "Stata _n is reserved; use _nobs"
    assert "scalar _nobs=e(N)" in model
    assert "(0) (_nobs) (_ng)" in model
    assert "else if _a2<0.05 {" in model and "else if _hp<0.05 {" in model
    assert 'local model_count = r(N)' in f["RUN_ALL.do"]
    assert 'MODEL_ESTIMATION_FAILURES=' in f["RUN_ALL.do"]
    assert "if `failures' | `estimation_failures' exit 459" in f["RUN_ALL.do"]
    for name,src in f.items():
        assert src.count("{")==src.count("}"),name
        assert "MODEL_SPEC_NOT_APPROVED" not in src,name
    print(json.dumps({"static_audit":"PASS","stata_executable_used":False,
                      "scenario_count":8,"files":sorted(f),
                      "warning":"Stata syntax/runtime and numerical results NOT verified."}))
if __name__=="__main__": main()
