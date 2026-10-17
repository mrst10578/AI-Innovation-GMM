* Called from 03/04; all results are explicitly preliminary until reviewed.
* Usage: do "stata/_run_one_model.do" <outcome> <safe_short_name>
version 16.0
args outcome slug
capture log close `slug'
log using "outputs/stata/`slug'.log", name(`slug') text replace
display as text "OUTCOME=`outcome'; independent models of unemployment and high-tech share."
local successful_gmm = 0
foreach cutoff in 2024 2023 {
    preserve
    keep if Year <= `cutoff'
    xtset panel_id Year, yearly
    local td "yr2017-yr2024"
    if `cutoff' == 2023 local td "yr2017-yr2023"
    display as result "======== SAMPLE END `cutoff' ========"
    quietly count
    display as result "INPUT_ROWS=" r(N)
    * Dynamic pooled OLS and within FE are biased comparison models, not causal benchmarks.
    capture noisily regress `outcome' L.`outcome' ln_ai_investment ln_ai_patents GDP_Growth `td', vce(cluster panel_id)
    if !_rc {
        estimates store `slug'_ols`cutoff'
        estimates save "outputs/stata/`slug'_ols`cutoff'.ster", replace
    }
    else display as error "POOLED OLS FAILED for `slug'/`cutoff'"
    capture noisily xtreg `outcome' L.`outcome' ln_ai_investment ln_ai_patents GDP_Growth `td', fe vce(cluster panel_id)
    if !_rc {
        estimates store `slug'_fe`cutoff'
        estimates save "outputs/stata/`slug'_fe`cutoff'.ster", replace
    }
    else display as error "DYNAMIC FE FAILED for `slug'/`cutoff'"
    * Collapse + a single lag depth restricts instrument proliferation at N=30.
    * One lag of L.y yields instruments dated no later than y_(t-2).
    * AI regressors are treated as endogenous, not proven exogenous.
    * GDP growth and year indicators are provisionally strictly exogenous: sensitivity needed.
    foreach system in system difference {
        foreach steps in onestep twostep {
            local eqopts ""
            local instruments "ivstyle(GDP_Growth `td', equation(both))"
            if "`system'" == "difference" {
                local eqopts "noleveleq"
                local instruments "ivstyle(GDP_Growth `td', equation(diff))"
            }
            display as result "GMM `slug' `cutoff' `system' `steps'"
            capture noisily xtabond2 `outcome' L.`outcome' ln_ai_investment ln_ai_patents GDP_Growth `td', ///
                gmmstyle(L.`outcome', laglimits(1 1) collapse) ///
                gmmstyle(ln_ai_investment ln_ai_patents, laglimits(2 2) collapse) ///
                `instruments' `eqopts' `steps' robust small
            local rc = _rc
            if `rc' {
                display as error "MODEL_FAILED outcome=`slug' cutoff=`cutoff' system=`system' step=`steps' rc=`rc'"
            }
            else {
                local successful_gmm = `successful_gmm' + 1
                local ident "`slug'_`system'_`steps'_`cutoff'"
                estimates store `ident'
                estimates save "outputs/stata/`ident'.ster", replace
                display as result "MODEL_EXECUTED_BUT_NOT_YET_VALIDATED `ident'"
                ereturn list
                matrix list e(b)
                * Hansen/Sargan, AR(1)/AR(2), instrument count and subset tests:
                * use actual xtabond2 output above; do not fabricate missing diagnostics.
            }
        }
    }
    restore
}
display as result "GMM_SUCCESSFUL_FITS=`successful_gmm' (fitness/identification STILL REQUIRES REVIEW)"
log close `slug'
if `successful_gmm' == 0 exit 459
