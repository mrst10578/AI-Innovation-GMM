* Export actual e() scalars captured during real xtabond2 execution.
version 16.0
preserve
capture confirm file "outputs/stata_model_summary.dta"
if _rc {
    restore
    exit 601
}
use "outputs/stata_model_summary.dta", clear
export delimited using "outputs/stata_model_summary.csv", replace
count
display as result "STATA_MODEL_ROWS=" r(N)
list, noobs
restore
