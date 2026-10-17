* Independent ASSOCIATIONAL alternatives, not proof of AI causality.
* Precommitted static two-way FE vs biased dynamic FE / dynamic OLS benchmarks.
* Source data, CHN/USA sensitivity and 2023 sensitivity are unchanged.
version 16.0
set more off
cd "D:/AI_Innovation_Stata_Ready"
capture log close _all
log using "outputs/stata/12_associational_fe.log", text replace
capture noisily do "stata/01_environment_and_data.do"
if _rc {
    display as error "SOURCE CHECK FAILED, no alternative fits executed."
    log close
    exit 459
}
postfile fe_post str35 model str25 outcome str18 family str8 exclusion double cutoff rc N Ng r2 lninv_b lninv_se lninv_p lnpat_b lnpat_se lnpat_p GDP_b GDP_se GDP_p lag_b lag_se lag_p using "outputs/stata/alternative_fe_models.dta", replace
local successes=0
local failures=0
foreach dep in HighTech_Exports Unemployment {
    local pref "hi"
    if "`dep'"=="Unemployment" local pref "un"
    foreach cutoff in 2024 2023 {
        foreach exclude in NONE CHN USA BOTH {
            preserve
            keep if Year<=`cutoff'
            if "`exclude'"=="CHN" drop if ISO3=="CHN"
            if "`exclude'"=="USA" drop if ISO3=="USA"
            if "`exclude'"=="BOTH" drop if inlist(ISO3,"CHN","USA")
            xtset panel_id Year
            local dums "yr2017-yr2024"
            if `cutoff'==2023 local dums "yr2017-yr2023"
            local label "`pref'_`cutoff'_`exclude'_staticFE"
            display as result "ALTERNATIVE_ATTEMPT=`label'"
            capture noisily xtreg `dep' ln_ai_investment ln_ai_patents GDP_Growth `dums', fe vce(cluster panel_id)
            local rc=_rc
            if `rc' {
                local failures=`failures'+1
                display as error "ALTERNATIVE_FAILED=`label' rc=`rc'"
                post fe_post ("`label'") ("`dep'") ("static_twFE") ("`exclude'") (`cutoff') (`rc') (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.)
            }
            else {
                local successes=`successes'+1
                local df=e(df_r)
                if missing(`df') | `df'<=0 local df=e(N_g)-1
                scalar invp=2*ttail(`df',abs(_b[ln_ai_investment]/_se[ln_ai_investment]))
                scalar patp=2*ttail(`df',abs(_b[ln_ai_patents]/_se[ln_ai_patents]))
                scalar gdpp=2*ttail(`df',abs(_b[GDP_Growth]/_se[GDP_Growth]))
                post fe_post ("`label'") ("`dep'") ("static_twFE") ("`exclude'") (`cutoff') (0) (e(N)) (e(N_g)) (e(r2_w)) (_b[ln_ai_investment]) (_se[ln_ai_investment]) (invp) (_b[ln_ai_patents]) (_se[ln_ai_patents]) (patp) (_b[GDP_Growth]) (_se[GDP_Growth]) (gdpp) (.) (.) (.)
                estimates save "outputs/stata/alternative_`label'.ster", replace
                display as result "ALTERNATIVE_FITTED=`label'"
            }
            restore
        }
        preserve
        keep if Year<=`cutoff'
        xtset panel_id Year
        local dums "yr2018-yr2024"
        if `cutoff'==2023 local dums "yr2018-yr2023"
        foreach family in dynamic_FE dynamic_OLS {
            local label "`pref'_`cutoff'_NONE_`family'"
            display as result "ALTERNATIVE_ATTEMPT=`label'"
            if "`family'"=="dynamic_FE" capture noisily xtreg `dep' L.`dep' ln_ai_investment ln_ai_patents GDP_Growth `dums', fe vce(cluster panel_id)
            else capture noisily regress `dep' L.`dep' ln_ai_investment ln_ai_patents GDP_Growth `dums', vce(cluster panel_id)
            local rc=_rc
            if `rc' {
                local failures=`failures'+1
                post fe_post ("`label'") ("`dep'") ("`family'") ("NONE") (`cutoff') (`rc') (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.) (.)
            }
            else {
                local successes=`successes'+1
                local df=e(df_r)
                if missing(`df') | `df'<=0 local df=29
                scalar invp=2*ttail(`df',abs(_b[ln_ai_investment]/_se[ln_ai_investment]))
                scalar patp=2*ttail(`df',abs(_b[ln_ai_patents]/_se[ln_ai_patents]))
                scalar gdpp=2*ttail(`df',abs(_b[GDP_Growth]/_se[GDP_Growth]))
                scalar lagp=2*ttail(`df',abs(_b[L.`dep']/_se[L.`dep']))
                local fitr2=e(r2)
                if "`family'"=="dynamic_FE" local fitr2=e(r2_w)
                post fe_post ("`label'") ("`dep'") ("`family'") ("NONE") (`cutoff') (0) (e(N)) (30) (`fitr2') (_b[ln_ai_investment]) (_se[ln_ai_investment]) (invp) (_b[ln_ai_patents]) (_se[ln_ai_patents]) (patp) (_b[GDP_Growth]) (_se[GDP_Growth]) (gdpp) (_b[L.`dep']) (_se[L.`dep']) (lagp)
                estimates save "outputs/stata/alternative_`label'.ster", replace
                display as result "ALTERNATIVE_FITTED=`label'"
            }
        }
        restore
    }
}
postclose fe_post
preserve
use "outputs/stata/alternative_fe_models.dta", clear
export delimited using "outputs/stata/alternative_fe_models.csv", replace
quietly count
display as result "ALTERNATIVE_ROWS=" r(N)
restore
display as result "ALTERNATIVE_SUCCESS_COUNT=" `successes'
display as result "ALTERNATIVE_FAILURE_COUNT=" `failures'
display as text "STATIC FE ASSOCIATION: not causal. Dynamic FE Nickell biased with T<=9. OLS biased with endogenous lag."
log close
if `successes'!=24 | `failures'!=0 exit 459
