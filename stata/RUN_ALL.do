* Execute from repository root on a licensed local Stata installation.
version 16.0
set more off
capture mkdir "outputs"
capture mkdir "data/processed"
capture log close _all
log using "outputs/stata_preflight.log", text replace
display as text "START STATA: " c(current_date) " " c(current_time)
display as result "Stata version " c(stata_version)
capture noisily do "stata/01_environment_and_data.do"
local rc = _rc
if `rc' {
    display as error "Preflight failure; no estimates claimed. Return code: `rc'"
    log close
    exit `rc'
}
capture noisily do "stata/02_pre_estimation.do"
if _rc display as error "Some short-panel diagnostics failed; inspect preflight log."
log close
do "stata/03_hightech_models.do"
do "stata/04_unemployment_models.do"
capture noisily do "stata/05_post_estimation_and_export.do"
display as result "Completed requested model scripts. Inspect logs for VALID/INVALID diagnostics."
