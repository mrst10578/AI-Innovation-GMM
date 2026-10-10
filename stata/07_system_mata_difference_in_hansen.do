* OPTIONAL SCIENTIFIC DIAGNOSTIC. Licensed Stata 16+ only.
* Distinct from successful V4 nomata fits: RUNS MATA path WITH split.
* No silent nomata fallback. No code-level declaration of causal validity.
version 16.0
clear all
set more off
capture mkdir "outputs"
capture log close _all
log using "outputs/AI_SYSTEM_DIFFERENCE_IN_HANSEN_MATA_ONLY.log", text replace
display as text "AI_SYSTEM_DH_AUDIT=OPTIONAL_LICENSED_MATA_RETEST"
display as text "DO_NOT_REPLACE_ORIGINAL_V4_OUTPUTS"
display as text "Run from extracted project root, Stata 16+, original Excel unchanged."
capture confirm file "data/raw/AI_Balanced_Panel (1).xlsx"
if _rc {
    display as error "MISSING_ORIGINAL_WORKBOOK"
    log close
    exit 601
}
capture noisily do "stata/01_environment_and_data.do"
local init_rc = _rc
if `init_rc' {
    display as error "SOURCE_DATA_PREFLIGHT_FAILED_RC=`init_rc'"
    log close
    exit `init_rc'
}
display as text "NOTE: THIS RUN DOES NOT TOUCH OR OVERRIDE THE NOMATA STUDY SUMMARY"
display as text "If r(3301) occurs, MATA is unavailable; do not claim D-H."
capture which xtabond2
if _rc {
    display as error "XTABOND2_UNAVAILABLE"
    log close
    exit 499
}
forvalues lastyear=2023/2024 {
    foreach y in HighTech_Exports Unemployment {
        preserve
        keep if Year<=`lastyear'
        quietly tabulate Year, generate(dh_year_)
        local tdums
        foreach x of varlist dh_year_* {
            if "`x'"!="dh_year_1" local tdums "`tdums' `x'"
        }
        display as text "BEGIN_REAL_MATA_DH `y' YEAR=`lastyear'"
        capture noisily xtabond2 `y' L.`y' ln1p_invest ln1p_patent GDP_Growth `tdums', ///
            gmmstyle(L.`y', lag(1 2) collapse split) ///
            gmmstyle(ln1p_invest, lag(2 3) collapse split) ///
            gmmstyle(ln1p_patent, lag(2 3) collapse split) ///
            gmmstyle(GDP_Growth, lag(2 3) collapse split) ///
            ivstyle(`tdums') twostep robust small
        local rc_mata = _rc
        display as result "REAL_MATA_DH_RUN_RC=`rc_mata' outcome=`y' year=`lastyear'"
        if `rc_mata' {
            display as error "DIFFERENCE_IN_HANSEN_NOT_EXECUTED: see source error above; no automatic fallback"
        }
        else {
            display as result "REAL_MATA_INSTRUMENTS=" e(j) " GROUPS=" e(N_g) " HANSEN_P=" e(hansenp) " AR2_P=" e(ar2p)
            display as text "ONLY THE ABOVE PRINTED xtabond2 Difference-in-Hansen subsets qualify as observed."
            display as text "SPLIT IS A REPORTING REQUEST, NOT A GUARANTEE OF IDENTIFICATION."
        }
        restore
    }
}
display as text "AI_SYSTEM_DH_END; send WHOLE outputs/AI_SYSTEM_DIFFERENCE_IN_HANSEN_MATA_ONLY.log"
log close
