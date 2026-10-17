* Winlator/Stata 17 direct execution from Android Downloads; propagate failures to caller.
version 16.0
set more off
capture log close _all
cd "D:/AI_Innovation_Stata_Ready"
capture mkdir "outputs"
capture mkdir "outputs/stata"
log using "outputs/stata/TABLET_BOOTSTRAP.log", name(ai_tablet) text replace
display as result "AI_TABLET_STATA_VERSION=" c(stata_version)
display as result "AI_TABLET_DATE=" c(current_date) " " c(current_time)
sysdir set PLUS "D:/AI_Innovation_Stata_Ready/plus/"
capture noisily mata: mata mlib index
display as result "MATA_INDEX_RC=" _rc
capture noisily which xtabond2
local ado_rc = _rc
display as result "XTABOND2_WHICH_RC=`ado_rc'"
if `ado_rc' {
    display as error "FATAL_XTABOND2_NOT_AVAILABLE"
    log close ai_tablet
    exit 499
}
capture confirm file "data/raw/AI_Balanced_Panel (1).xlsx"
if _rc {
    display as error "FATAL_INSTRUCTOR_EXCEL_MISSING"
    log close ai_tablet
    exit 601
}
log close ai_tablet
capture noisily do "stata/RUN_ALL.do"
local result_rc = _rc
capture log close _all
log using "outputs/stata/TABLET_FINISH_STATUS.log", name(ai_final) text replace
display as result "AI_STATA_REAL_EXECUTION_RETURN_CODE=`result_rc'"
capture confirm file "outputs/stata/hightech.log"
display as result "HIGHTECH_LOG_PRESENT=" (_rc==0)
capture confirm file "outputs/stata/unemployment.log"
display as result "UNEMPLOYMENT_LOG_PRESENT=" (_rc==0)
if `result_rc' display as error "AI_STATA_RUN_FAILED; do NOT publish partial model results."
else display as result "AI_STATA_ALL_BASELINE_EXECUTED; causal interpretation remains conditional."
log close ai_final
if `result_rc' exit `result_rc'
