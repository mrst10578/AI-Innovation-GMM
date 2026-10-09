* Exact inputs: outcome endyear difference|system. All fitted models require review.
version 16.0
args y endyear method
if !inlist("`y'", "HighTech_Exports", "Unemployment") exit 198
if !inlist("`endyear'", "2023", "2024") exit 198
if !inlist("`method'", "difference", "system") exit 198
preserve
keep if Year <= real("`endyear'")
isid ISO3 Year
quietly tabulate Year, generate(yrd_)
local times
foreach v of varlist yrd_* {
    if "`v'" != "yrd_1" local times "`times' `v'"
}
capture log close _all
log using "outputs/AI_`y'_`endyear'_`method'.log", text replace
display as text "SPEC: outcome=`y' years=2016-`endyear' method=`method'"
display as text "Collapsed GMM: lagged outcome t-2:t-3; all AI and GDP t-2:t-3; year effects."
display as text "All non-time regressors provisionally endogenous; System adds extra level moment assumptions."
* This sample has 30 countries and at most nine years. Use dense Mata
* to avoid the space-streaming matrix-indexing path. If it fails with 3301,
* transparently retry the SAME GMM specification using the ado implementation.
capture noisily mata: mata set matafavor speed
local mata_setting_rc = _rc
if `mata_setting_rc' display as error "MATA_SPEED_SETTING_FAILED RC=" `mata_setting_rc'
local engine "MATA_SPEED"
local engine_option ""
local fallback_used = 0
local rc = 3301
forvalues attempt = 1/2 {
    if `attempt' == 1 | (`attempt' == 2 & `rc' == 3301) {
        if `attempt' == 2 {
            local engine "ADO_NOMATA"
            local engine_option "nomata"
            local fallback_used = 1
            display as error "MATA_3301_RETRY_WITH_NOMATA: results need independent review"
            display as text "NOTE: nomata does not report Difference-in-Hansen tests."
        }
        display as text "ESTIMATION_ENGINE=`engine'"
        if "`method'"=="difference" {
            capture noisily xtabond2 `y' L.`y' ln1p_invest ln1p_patent GDP_Growth `times', ///
                gmmstyle(L.`y', lag(1 2) collapse) ///
                gmmstyle(ln1p_invest, lag(2 3) collapse) ///
                gmmstyle(ln1p_patent, lag(2 3) collapse) ///
                gmmstyle(GDP_Growth, lag(2 3) collapse) ///
                ivstyle(`times', equation(diff)) noleveleq twostep robust small `engine_option'
            local rc = _rc
        }
        else {
            capture noisily xtabond2 `y' L.`y' ln1p_invest ln1p_patent GDP_Growth `times', ///
                gmmstyle(L.`y', lag(1 2) collapse split) ///
                gmmstyle(ln1p_invest, lag(2 3) collapse split) ///
                gmmstyle(ln1p_patent, lag(2 3) collapse split) ///
                gmmstyle(GDP_Growth, lag(2 3) collapse split) ///
                ivstyle(`times') twostep robust small `engine_option'
            local rc = _rc
        }
        display as text "ENGINE_RC=`rc' (0 means an estimate returned, not scientific validity)"
    }
}
if `rc' {
    display as error "GMM_ESTIMATION_FAILED RC=" `rc'
    post __audit ("`y'") ("`endyear'") ("`method'") ("EXECUTION_FAILED") ///
        (`rc') (.) (.) (.) (.) (.) (.) (.) (.) (.)
}
else {
    scalar _nobs=e(N)
    scalar _ng=e(N_g)
    scalar _j=e(j)
    scalar _hd=e(hansen_df)
    scalar _hp=e(hansenp)
    scalar _sd=e(sar_df)
    scalar _sp=e(sarganp)
    scalar _a1=e(ar1p)
    scalar _a2=e(ar2p)
    local status "REVIEW_REQUIRED"
    if `fallback_used' local status "REVIEW_ADO_FALLBACK"
    if missing(_j) | missing(_ng) | _j>=_ng local status "INVALID_INSTRUMENTS"
    if missing(_a2) {
        local status "INVALID_AR2_MISSING"
    }
    else if _a2<0.05 {
        local status "INVALID_AR2_REJECTED"
    }
    if missing(_hd) | _hd<=0 | missing(_hp) {
        local status "INVALID_HANSEN_DF"
    }
    else if _hp<0.05 {
        local status "INVALID_HANSEN_REJECTED"
    }
    display as result "AUDIT_STATUS=`status' ENGINE=`engine'"
    if `fallback_used' display as error "ADO_FALLBACK_NOT_EQUIVALENCE_CERTIFIED: Difference-in-Hansen unavailable"
    display as text "Number of instruments=" _j " groups=" _ng " observations=" _nobs
    display as text "Hansen df=" _hd " p=" _hp " Sargan df=" _sd " p=" _sp
    display as text "AR1 p=" _a1 " AR2 p=" _a2
    display as text "System subset Difference-in-Hansen, if identifiable, appears in xtabond2 log."
    capture noisily estimates save "outputs/AI_`y'_`endyear'_`method'.ster", replace
    post __audit ("`y'") ("`endyear'") ("`method'") ("`status'") ///
        (0) (_nobs) (_ng) (_j) (_hd) (_hp) (_sd) (_sp) (_a1) (_a2)
}
log close
restore
