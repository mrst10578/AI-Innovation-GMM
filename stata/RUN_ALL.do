* Strict orchestration; all expected 16 baseline models and mandatory diagnostics must complete.
* Always execute against the original instructor-supplied workbook, not a pre-existing DTA.
version 16.0
clear all
set more off
set linesize 120
capture mkdir "outputs"
capture mkdir "outputs/stata"
capture log close _all
log using "outputs/stata/00_master.log", name(master) text replace
display as result "STATA_VERSION=" c(stata_version)
display as result "STARTED=" c(current_date) " " c(current_time)
capture noisily do "stata/01_environment_and_data.do"
local rc = _rc
if `rc' {
    display as error "FATAL_SOURCE_PREFLIGHT_FAILED rc=`rc'"
    log close master
    exit `rc'
}
capture which xtabond2
if _rc {
    display as error "FATAL_XTABOND2_PACKAGE_MISSING"
    log close master
    exit 499
}
capture noisily do "stata/02_pre_estimation.do"
local pre_rc = _rc
if `pre_rc' {
    display as error "FATAL_PRE_ESTIMATION_DIAGNOSTICS_FAILED rc=`pre_rc'"
    log close master
    exit `pre_rc'
}
postfile ai_post str36 model str24 status double rc N Ng instruments sargan_p hansen_p ar1_p ar2_p using "outputs/stata/gmm_diagnostics.dta", replace
capture noisily do "stata/03_hightech_models.do"
local rc1 = _rc
if `rc1' {
    display as error "FATAL_HIGHTECH_GMM_BATCH_FAILED rc=`rc1'"
    capture postclose ai_post
    log close master
    exit `rc1'
}
capture noisily do "stata/04_unemployment_models.do"
local rc2 = _rc
if `rc2' {
    display as error "FATAL_UNEMPLOYMENT_GMM_BATCH_FAILED rc=`rc2'"
    capture postclose ai_post
    log close master
    exit `rc2'
}
capture noisily do "stata/05_post_estimation_and_export.do"
local export_rc = _rc
if `export_rc' {
    display as error "FATAL_POST_ESTIMATION_EXPORT_FAILED rc=`export_rc'"
    capture postclose ai_post
    log close master
    exit `export_rc'
}
preserve
use "outputs/stata/gmm_diagnostics.dta", clear
quietly count
local total = r(N)
quietly count if rc != 0
local failed = r(N)
restore
if `total' != 16 | `failed' != 0 {
    display as error "FATAL_INCOMPLETE_GMM_BATCH total=`total' failed=`failed' expected=16"
    log close master
    exit 459
}
display as result "STATA_REQUIRED_PRETESTS_COMPLETE=1"
display as result "STATA_GMM_ALL_16_COMPLETE=1"
display as result "FINISHED=" c(current_date) " " c(current_time)
log close master
