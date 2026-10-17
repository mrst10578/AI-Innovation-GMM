* Entry point: run from repository root, in genuinely licensed Stata.
* This is executable model code but is NOT proof a Stata estimation was run.
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
display as text "Logs reflect only executions actually made by licensed Stata."
capture noisily do "stata/01_environment_and_data.do"
local rc = _rc
if `rc' {
    display as error "DATA PREFLIGHT FAILED, rc=`rc'; no GMM attempted."
    log close master
    exit `rc'
}
capture which xtabond2
if _rc {
    display as error "xtabond2 unavailable. With network access run: ssc install xtabond2, replace"
    log close master
    exit 499
}
display as text "xtabond2 found at: " "stata/xtabond2"
capture noisily do "stata/02_pre_estimation.do"
if _rc display as error "Pre-estimation script returned code " _rc
capture noisily do "stata/03_hightech_models.do"
local rc1 = _rc
if `rc1' display as error "HighTech model script failed: rc=`rc1'"
capture noisily do "stata/04_unemployment_models.do"
local rc2 = _rc
if `rc2' display as error "Unemployment model script failed: rc=`rc2'"
do "stata/05_post_estimation_and_export.do"
display as result "FINISHED=" c(current_date) " " c(current_time)
log close master
if `rc1' exit `rc1'
if `rc2' exit `rc2'
