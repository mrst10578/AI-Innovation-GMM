* Prespecified geographic influence check (12 fits). See docs/STATA_INFLUENCE_PREREG_20261017.md
* Original 2026-10-17 2-step SYSTEM GMM specification unchanged except country exclusions.
version 16.0
set more off
cd "D:/AI_Innovation_Stata_Ready"
capture log close _all
log using "outputs/stata/09_influence_china_usa.log", text replace
display as result "INFLUENCE_STARTED=" c(current_date) " " c(current_time)
capture noisily do "stata/01_environment_and_data.do"
local rc=_rc
if `rc' {
    display as error "INFLUENCE_SOURCE_CHECK_FAILED rc=`rc'"
    log close
    exit `rc'
}
capture which xtabond2
if _rc {
    display as error "XTABOND2_UNAVAILABLE"
    log close
    exit 499
}
postfile loo str28 model str12 dropped str22 outcome double cutoff rc N Ng instruments sargan_p hansen_p ar1_p ar2_p lag_b inv_b patent_b gdp_b using "outputs/stata/influence_v1.dta", replace
local successes=0
local fails=0
foreach dep in HighTech_Exports Unemployment {
    local short "hi"
    if "`dep'"=="Unemployment" local short "un"
    foreach cutoff in 2024 2023 {
        local td "yr2017-yr2024"
        if `cutoff'==2023 local td "yr2017-yr2023"
        foreach drop in CHN USA BOTH {
            preserve
            keep if Year<=`cutoff'
            if "`drop'"=="CHN" drop if ISO3=="CHN"
            if "`drop'"=="USA" drop if ISO3=="USA"
            if "`drop'"=="BOTH" drop if inlist(ISO3,"CHN","USA")
            xtset panel_id Year
            local tag "`short'_`cutoff'_`drop'"
            display as result "INFLUENCE_ATTEMPT=`tag'"
            quietly count
            display as result "INFLUENCE_INPUT_N=" r(N)
            capture noisily xtabond2 `dep' L.`dep' ln_ai_investment ln_ai_patents GDP_Growth `td', ///
                gmmstyle(L.`dep', laglimits(1 1) collapse) ///
                gmmstyle(ln_ai_investment ln_ai_patents, laglimits(2 2) collapse) ///
                ivstyle(GDP_Growth `td', equation(both)) twostep robust small
            local rc=_rc
            if `rc' {
                local fails=`fails'+1
                display as error "INFLUENCE_FAILED=`tag' rc=`rc'"
                post loo ("`tag'") ("`drop'") ("`dep'") (`cutoff') (`rc') (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.)
            }
            else {
                local successes=`successes'+1
                post loo ("`tag'") ("`drop'") ("`dep'") (`cutoff') (0) (e(N)) (e(N_g)) (e(j)) (e(sarganp)) (e(hansenp)) (e(ar1p)) (e(ar2p)) (_b[L.`dep']) (_b[ln_ai_investment]) (_b[ln_ai_patents]) (_b[GDP_Growth])
                display as result "INFLUENCE_FITTED=`tag' Ng=" e(N_g) " inst=" e(j) " Hansen=" e(hansenp) " AR2=" e(ar2p)
                estimates save "outputs/stata/influence_`tag'.ster", replace
            }
            restore
        }
    }
}
postclose loo
preserve
use "outputs/stata/influence_v1.dta", clear
export delimited using "outputs/stata/influence_v1.csv", replace
quietly count
display as result "INFLUENCE_ROWS=" r(N)
restore
display as result "INFLUENCE_FITS=" `successes' " INFLUENCE_FAILURES=" `fails'
display as text "All influence variants remain scientific HOLD."
display as result "INFLUENCE_FINISHED=" c(current_date) " " c(current_time)
log close
if `successes' != 12 | `fails' != 0 {
    display as error "STRICT_COUNTRY_INFLUENCE_INCOMPLETE: expected 12, got `successes', failures `fails'"
    exit 459
}
