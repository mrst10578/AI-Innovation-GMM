"""Static contract for optional genuinely licensed difference-in-Hansen script.
Passing this check never means Stata was run or a test was numerically observed.
"""
from pathlib import Path
p=Path("stata/07_system_mata_difference_in_hansen.do")
s=p.read_text(encoding="utf-8")
assert "REAL_MATA_DH_RUN_RC=" in s and "DIFFERENCE_IN_HANSEN_NOT_EXECUTED" in s
assert "split)" in s and "twostep robust small" in s
assert "forvalues lastyear=2023/2024" in s
assert "foreach y in HighTech_Exports Unemployment" in s
assert "nomata" not in "".join(v for v in s.splitlines() if not v.strip().startswith("*") and not v.strip().startswith("display"))
assert "outputs/AI_SYSTEM_DIFFERENCE_IN_HANSEN_MATA_ONLY.log" in s
print("STATA_MATA_DIFFERENCE_IN_HANSEN_STATIC_CONTRACT_PASS")
print("IMPORTANT: UNEXECUTED WITHOUT LICENSED STATA; NEVER CLAIM D-H PVALUES")
