# R-script sensitivity audit (source-based; does NOT execute R)
from pathlib import Path
s=Path("src/r/sensitivity_ai_china.R").read_text(encoding="utf-8")
assert "nrow(df)==270" in s and "!=\"CHN\"" in s
assert "last_year in c(2024,2023)" in s and "trans in c(\"d\",\"ld\")" in s
assert "max_lag in c(2,3)" in s and "exclude_china in c(FALSE,TRUE)" in s
assert "length(rows)==32" in s and "write.csv(out" in s
print("STATIC_R_SENSITIVITY_SPEC=32; R runtime CI separately required")
