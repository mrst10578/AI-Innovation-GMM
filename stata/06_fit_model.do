* AI Innovation study: explicit non-Mata recovery path for xtabond2 Mata 3301.
* All estimates are REVIEW ONLY. No programmatic inference of causal validity.
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
display as text "AI_GMM_FIX_ID=V4_3301_198_NOMATA"
display as text "SPEC outcome=`y' period=2016-`endyear' method=`method'"
display as text "NONMATA_FIRST: explicitly avoids xtabond2_mata() r(3301)."
display as text "All regressors AI and GDP provisionally endogenous; assumptions NOT source-validated."
display as text "NO_AUTOMATIC_MATA_FALLBACK: do NOT interpret a successful estimate as a valid GMM model."
display as text "Difference-in-Hansen is not available in nomata implementation."
local engine "ADO_NOMATA"
local model_rc = .

* Keep instrument, lag, estimator and year-control specifications unchanged.
* Substituting nomata changes computation engine, not a declaration of validity.
if "`method'" == "difference" {
    capture noisily xtabond2 `y' L.`y' ln1p_invest ln1p_patent GDP_Growth `times', ///
        gmmstyle(L.`y', lag(1 2) collapse) ///
        gmmstyle(ln1p_invest, lag(2 3) collapse) ///
        gmmstyle(ln1p_patent, lag(2 3) collapse) ///
        gmmstyle(GDP_Growth, lag(2 3) collapse) ///
        ivstyle(`times', equation(diff)) noleveleq twostep robust small nomata
    local model_rc = _rc
}
* xtabond2_stata (nomata) rejects split inside gmmstyle() with r(198).
* split changes Difference-in-Hansen reporting only, unavailable in nomata.
else {
    capture noisily xtabond2 `y' L.`y' ln1p_invest ln1p_patent GDP_Growth `times', ///
        gmmstyle(L.`y', lag(1 2) collapse) ///
        gmmstyle(ln1p_invest, lag(2 3) collapse) ///
        gmmstyle(ln1p_patent, lag(2 3) collapse) ///
        gmmstyle(GDP_Growth, lag(2 3) collapse) ///
        ivstyle(`times') twostep robust small nomata
    local model_rc = _rc
}
display as result "GMM_ESTIMATION_RC=" `model_rc' " ENGINE=`engine'"

if `model_rc' {
    display as error "MODEL_ESTIMATION_FAILED: read full AI_*.log; no fabricated results."
    post __audit ("`y'") ("`endyear'") ("`method'") ("EXECUTION_FAILED") ///
        ("`engine'") ("ESTIMATION_FAILED") ///
        (`model_rc') (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
        (.) (.) (.) (.) (.) (.)
}
else {
    * Stata reserved _n must never be reused as a scalar name.
    scalar sc_nobs = e(N)
    scalar sc_ng = e(N_g)
    scalar sc_j = e(j)
    scalar sc_hd = e(hansen_df)
    scalar sc_hp = e(hansenp)
    scalar sc_sd = e(sar_df)
    scalar sc_sp = e(sarganp)
    scalar sc_a1 = e(ar1p)
    scalar sc_a2 = e(ar2p)

    * An omitted regressor produces missing coefficient, not a fake zero.
    scalar sc_invest_b = .
    scalar sc_invest_se = .
    scalar sc_patent_b = .
    scalar sc_patent_se = .
    scalar sc_gdp_b = .
    scalar sc_gdp_se = .
    capture scalar sc_invest_b = _b[ln1p_invest]
    capture scalar sc_invest_se = _se[ln1p_invest]
    capture scalar sc_patent_b = _b[ln1p_patent]
    capture scalar sc_patent_se = _se[ln1p_patent]
    capture scalar sc_gdp_b = _b[GDP_Growth]
    capture scalar sc_gdp_se = _se[GDP_Growth]

    * Independent flags: none of these tests can overwrite another.
    local flags "NO_DIFFERENCE_HANSEN;SOURCE_UNVERIFIED"
    if missing(sc_j) | missing(sc_ng) | sc_j>=sc_ng {
        local flags "`flags';INSTRUMENT_COUNT"
    }
    if missing(sc_a1) {
        local flags "`flags';AR1_MISSING"
    }
    else if sc_a1 >= 0.05 {
        local flags "`flags';AR1_NONREJECTION"
    }
    if missing(sc_a2) {
        local flags "`flags';AR2_MISSING"
    }
    else if sc_a2 < 0.05 {
        local flags "`flags';AR2_REJECTED"
    }
    if missing(sc_hd) | sc_hd<=0 | missing(sc_hp) {
        local flags "`flags';HANSEN_UNTESTABLE"
    }
    else {
        if sc_hp<0.05 local flags "`flags';HANSEN_REJECTED"
        if sc_hp>0.99 local flags "`flags';HANSEN_SUSPICIOUS_HIGH"
    }
    if missing(sc_invest_b) | missing(sc_patent_b) {
        local flags "`flags';AI_COEFFICIENT_MISSING"
    }
    local status "REVIEW_REQUIRED"
    * Clearly reject models with failed essential diagnostics; otherwise still unapproved.
    if missing(sc_j) | missing(sc_ng) | sc_j>=sc_ng | missing(sc_a2) | missing(sc_hd) | sc_hd<=0 | missing(sc_hp) {
        local status "NOT_APPROVED"
    }
    else if sc_a2<0.05 | sc_hp<0.05 {
        local status "NOT_APPROVED"
    }
    * NO model is ever marked APPROVED by code.
    display as error "MODEL_REQUIRES_SCIENTIFIC_REVIEW flags=`flags'"
    display as result "INSTRUMENTS=" sc_j " GROUPS=" sc_ng " OBS=" sc_nobs
    display as result "HANSEN_P=" sc_hp " AR1_P=" sc_a1 " AR2_P=" sc_a2

    * Check actual storage result, rather than using capture without auditing.
    capture noisily estimates save "outputs/AI_`y'_`endyear'_`method'.ster", replace
    local save_rc = _rc
    if `save_rc' {
        local flags "`flags';ESTIMATES_SAVE_FAILED"
        display as error "ESTIMATES_SAVE_FAILED RC=" `save_rc'
    }
    post __audit ("`y'") ("`endyear'") ("`method'") ("`status'") ///
        ("`engine'") ("`flags'") ///
        (0) (sc_nobs) (sc_ng) (sc_j) (sc_hd) (sc_hp) (sc_sd) (sc_sp) (sc_a1) (sc_a2) ///
        (sc_invest_b) (sc_invest_se) (sc_patent_b) (sc_patent_se) (sc_gdp_b) (sc_gdp_se)
}
log close
restore
