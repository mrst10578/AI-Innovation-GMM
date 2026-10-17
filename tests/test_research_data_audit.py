"""Regression checks on committed source data, separate from Stata availability."""
from pathlib import Path
import json
import pandas as pd
from src.python.preflight import ROOT, audit_dataframe

def test_source_is_unchanged_and_panel_keys_are_unique():
    cfg=json.loads((ROOT/"config/project.json").read_text(encoding="utf-8"))
    df=pd.read_excel(ROOT/"data/raw"/cfg["source_workbook"])
    result=audit_dataframe(df,cfg)
    assert result["status"]=="ready_for_methodology_audit"
    assert result["balanced"] is True
    assert result["rows"]==270 and result["countries"]==30
    assert result["duplicate_keys"]==0
    assert df.loc[df.ISO3=="IRN"].empty

def test_2024_patent_drop_recomputes_from_source():
    cfg=json.loads((ROOT/"config/project.json").read_text(encoding="utf-8"))
    df=pd.read_excel(ROOT/"data/raw"/cfg["source_workbook"])
    p=df.pivot(index="ISO3",columns="Year",values="AI_Patents")
    assert int((p[2024]<p[2023]).sum())==26
    assert int((df.AI_Investment==0).sum())==5

def test_stata_entrypoints_include_real_xtabond2_not_placeholder():
    source=(ROOT/"stata/_run_one_model.do").read_text(encoding="utf-8")
    assert "xtabond2" in source
    assert "gmmstyle" in source and "laglimits(2 2) collapse" in source
    assert "noleveleq" in source and "twostep" in source
    assert "onestep robust" not in source # default = one-step
    assert "MODEL_EXECUTED_BUT_NOT_YET_VALIDATED" in source
    for file in ["01_environment_and_data.do","02_pre_estimation.do",
                 "03_hightech_models.do","04_unemployment_models.do",
                 "05_post_estimation_and_export.do"]:
        assert (ROOT/"stata"/file).is_file()
