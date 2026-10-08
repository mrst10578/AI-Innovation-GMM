* Prepared for real licensed Stata; script execution is not certification.
version 16.0
clear all
set more off
capture log close _all
capture mkdir "outputs"
capture mkdir "data/processed"
log using "outputs/stata_preflight.log", text replace
display as text "Stata version " c(stata_version)
capture noisily do "stata/01_environment_and_data.do"
local pre_rc = _rc
if `pre_rc' {
    display as error "FATAL PREFLIGHT RC=" `pre_rc'
    log close
    exit `pre_rc'
}
capture noisily do "stata/02_pre_estimation.do"
local pretests_rc = _rc
if `pretests_rc' display as error "PRETESTS ERROR RC=" `pretests_rc'
log close
postfile __audit str22 outcome str4 period str12 method str32 status ///
    double rc n groups instruments hdf hp sdf sp ar1p ar2p ///
    using "outputs/stata_model_summary.dta", replace
local failures = 0
capture noisily do "stata/03_hightech_models.do"
local rc_a = _rc
if `rc_a' local failures = `failures' + 1
capture noisily do "stata/04_unemployment_models.do"
local rc_b = _rc
if `rc_b' local failures = `failures' + 1
postclose __audit
capture noisily do "stata/05_post_estimation_and_export.do"
local rc_export = _rc
if `rc_export' local failures = `failures' + 1
display as result "MODEL_SCRIPT_FAILURES=" `failures'
display as text "Review outputs/stata_model_summary.csv and individual outputs/AI_*.log"
if `failures' exit 459
