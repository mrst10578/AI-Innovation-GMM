* Model-specific logs and .ster files are saved by _run_one_model.do.
postclose ai_post
preserve
use "outputs/stata/gmm_diagnostics.dta", clear
export delimited using "outputs/stata/gmm_diagnostics.csv", replace
quietly count
local record_count = r(N)
quietly count if rc != 0
local failed_count = r(N)
display as result "STATA_DIAGNOSTIC_RECORDS=`record_count' FAILED=`failed_count'"
if `record_count' != 16 | `failed_count' != 0 {
    display as error "FATAL_INCOMPLETE_DIAGNOSTIC_CSV"
    restore
    exit 459
}
restore
* Post-estimation diagnostics printed by xtabond2 must be inspected per specification.
* Do not treat statistical insignificance of AR(2) or Hansen alone as proof of validity.
display as text "OUTPUT: outputs/stata/hightech.log and outputs/stata/unemployment.log"
display as text "GMM status remains REVIEW_PENDING until instrument count < groups,"
display as text "AR(2) and overidentification diagnostics are examined, and missing tests documented."
display as text "Difference-in-Hansen is available only if reported for appropriate nested instrument subsets."
display as text "Sensitivity: 2016-2023 is separately stored; do not silently discard 2024."
