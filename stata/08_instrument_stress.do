* Pre-registered second-round tests: read docs/STATA_FOLLOWUP_PREREG_20261017.md
* Run from Winlator with D: mapped to Android Downloads.
version 16.0
set more off
cd "D:/AI_Innovation_Stata_Ready"
capture mkdir "outputs"
capture mkdir "outputs/stata"
capture log close _all
log using "outputs/stata/08_instrument_stress.log", text replace
display as result "STATA_SENSITIVITY_ROUND2_START " c(current_date) " " c(current_time)
capture noisily do "stata/01_environment_and_data.do"
local rc = _rc
if `rc' {
    display as error "SECOND_ROUND_DATA_PREFLIGHT_FAILED rc=`rc'"
    log close
    exit `rc'
}
capture which xtabond2
if _rc {
    display as error "xtabond2 missing; previously staged Winlator PLUS directory required."
    log close
    exit 499
}
postfile ai2 str32 model str24 status double rc N Ng instruments sargan_p hansen_p ar1_p ar2_p lag_b inv_b patents_b gdp_b using "outputs/stata/stress_v2_diagnostics.dta", replace
local fit_count = 0
local failed_count = 0
foreach dep in HighTech_Exports Unemployment {
    local prefix "hi"
    if "`dep'"=="Unemployment" local prefix "un"
    foreach cutoff in 2024 2023 {
        preserve
        keep if Year<=`cutoff'
        xtset panel_id Year
        local td "yr2018-yr2024"
        if `cutoff'==2023 local td "yr2018-yr2023"
        foreach spec in D23_X D23_E S23_X S23_E {
            local tag "`prefix'_`cutoff'_`spec'"
            local eq "noleveleq"
            local controls "ivstyle(GDP_Growth `td', equation(diff))"
            local gdp ""
            if strpos("`spec'","_E")>0 {
                local gdp "gmmstyle(GDP_Growth, laglimits(2 3) collapse)"
                local controls "ivstyle(`td', equation(diff))"
            }
            if substr("`spec'",1,1)=="S" {
                local eq ""
                local controls "ivstyle(GDP_Growth `td', equation(both))"
                if strpos("`spec'","_E")>0 local controls "ivstyle(`td', equation(both))"
            }
            display as result "STRESS_ATTEMPT=`tag' (prior specification; do not cherry-pick)"
            capture noisily xtabond2 `dep' L.`dep' ln_ai_investment ln_ai_patents GDP_Growth `td', ///
                gmmstyle(L.`dep', laglimits(1 2) collapse) ///
                gmmstyle(ln_ai_investment ln_ai_patents, laglimits(2 3) collapse) ///
                `gdp' `controls' `eq' twostep robust small
            local rc = _rc
            if `rc' {
                local failed_count = `failed_count'+1
                display as error "STRESS_FAILED=`tag' rc=`rc'"
                post ai2 ("`tag'") ("FAILED") (`rc') (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.)
            }
            else {
                local fit_count = `fit_count'+1
                local status "SCIENTIFIC_HOLD"
                if missing(e(j),e(N_g),e(ar2p),e(hansenp)) local status "DIAGNOSTIC_HOLD"
                if !missing(e(j),e(N_g),e(ar2p),e(hansenp)) {
                    if e(j)>=e(N_g) | e(ar2p)<0.05 | e(hansenp)<0.05 | e(hansenp)>.95 local status "DIAGNOSTIC_HOLD"
                }
                post ai2 ("`tag'") ("`status'") (0) (e(N)) (e(N_g)) (e(j)) (e(sarganp)) (e(hansenp)) (e(ar1p)) (e(ar2p)) (_b[L.`dep']) (_b[ln_ai_investment]) (_b[ln_ai_patents]) (_b[GDP_Growth])
                display as result "STRESS_FITTED=`tag' status=`status' N=" e(N) " inst=" e(j) " Hansen=" e(hansenp) " AR2=" e(ar2p)
                estimates save "outputs/stata/stress_`tag'.ster", replace
                ereturn list
            }
        }
        restore
    }
}
postclose ai2
preserve
use "outputs/stata/stress_v2_diagnostics.dta", clear
export delimited using "outputs/stata/stress_v2_diagnostics.csv", replace
quietly count
display as result "STRESS_DIAGNOSTIC_ROWS=" r(N)
restore
display as result "STRESS_FITS=" `fit_count' " STRESS_FAILURES=" `failed_count'
display as text "Every model remains scientific HOLD until independently assessed."
display as result "STATA_SENSITIVITY_ROUND2_FINISHED " c(current_date) " " c(current_time)
log close
if `fit_count'==0 exit 459
