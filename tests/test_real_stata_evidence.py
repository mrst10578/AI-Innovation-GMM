"""Static consistency checks on archived *actual* Stata outputs.
No Stata engine is invoked by these tests; they do not establish causal identification.
"""
import csv
import json
from pathlib import Path
from src.python.preflight import ROOT

R=ROOT/"reports"
def rows(name):
    with (R/name).open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def test_actual_run_counts_and_identifiers():
    base=rows("STATA_REAL_gmm_diagnostics_20261017.csv")
    stress=rows("STATA_REAL_stress_v2_20261017.csv")
    loo=rows("STATA_REAL_influence_CHN_USA_20261017.csv")
    wald=rows("STATA_REAL_joint_hypotheses_20261017.csv")
    assert (len(base),len(stress),len(loo),len(wald))==(16,16,12,16)
    for group in (base,stress,loo,wald):
        names=[r["model"] for r in group]
        assert len(set(names))==len(names)
        assert all(int(r["rc"])==0 for r in group)
    assert all(int(r["groups"])==30 for r in wald)
    assert all(int(r["Ng"]) in (28,29) for r in loo)
    assert all(int(r["Ng"])==30 for r in stress)
    assert all(r["hansen_p"] and r["ar2_p"] for r in stress)
    assert all(r["joint_ai_p"] and r["persistence_equal1_p"] for r in wald)

def test_recorded_coefficients_are_complete():
    old=rows("STATA_REAL_coefficients_20261017.csv")
    new=rows("STATA_REAL_followup_coefficients_20261017.csv")
    assert len(old)==64
    assert len(new)==112
    assert len({x["model"] for x in new})==28
    for x in new:
        assert x["se"] and x["estimate"] and x["p_value"]
    assert all(float(x["p_value"])>=.05 for x in new if x["term"]=="ln_ai_investment")
    # No multiplicity correction is claimed for this one unreplicated single-coefficient result.
    assert sum(float(x["p_value"])<.05 for x in new if x["term"]=="ln_ai_patents")==1

def test_source_concentration_and_method_warnings():
    src=json.loads((R/"source_concentration_20261017.json").read_text(encoding="utf-8"))
    assert src["n_countries"]==30 and src["n_rows"]==270
    patents=src["metrics"]["AI_Patents"]
    inv=src["metrics"]["AI_Investment"]
    assert patents["country_declines_2024"]==26
    assert patents["country_growth_2024"]["CHN"]==260214.0
    assert 0.92<patents["by_year"]["2024"]["largest_country_share"]<0.921
    assert 0.715<inv["by_year"]["2024"]["largest_country_share"]<0.716
    stress_log=(R/"STATA_REAL_instrument_stress_v2_20261017.log").read_text(encoding="utf-8")
    influence_log=(R/"STATA_REAL_influence_CHN_USA_20261017.log").read_text(encoding="utf-8")
    assert "STRESS_FITS=16 STRESS_FAILURES=0" in stress_log
    assert "INFLUENCE_FITS=12 INFLUENCE_FAILURES=0" in influence_log
    assert "covariance matrix of moments is singular" not in stress_log
    assert influence_log.count("covariance matrix of moments is singular")==12
    assert stress_log.count("Difference-in-Hansen tests of exogeneity of instrument subsets:")==16
