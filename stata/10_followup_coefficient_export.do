* Extract SE and t-based intervals from 28 actual second-round Stata estimate files.
* No refitting or p-value-based model choice. Matrices already saved in .ster.
version 16.0
set more off
cd "D:/AI_Innovation_Stata_Ready"
capture log close _all
log using "outputs/stata/10_followup_coefficient_export.log", text replace
postfile coef2 str36 model str28 term double estimate se t_value p_value ci95_low ci95_high nobs groups using "outputs/stata/followup_coefficients.dta", replace
local successes=0
local missingfits=0
foreach outcome in HighTech_Exports Unemployment {
    local prefix "hi"
    if "`outcome'"=="Unemployment" local prefix "un"
    foreach cutoff in 2024 2023 {
        foreach spec in D23_X D23_E S23_X S23_E {
            local tag "stress_`prefix'_`cutoff'_`spec'"
            capture noisily estimates use "outputs/stata/`tag'.ster"
            if _rc {
                local missingfits=`missingfits'+1
                display as error "MISSING_STRESS_ESTIMATE=`tag'"
            }
            else {
                local successes=`successes'+1
                local ng=e(N_g)
                local n=e(N)
                local df=e(df_r)
                if missing(`df') | `df'<=0 local df=`ng'-1
                foreach term in L.`outcome' ln_ai_investment ln_ai_patents GDP_Growth {
                    capture scalar eb=_b[`term']
                    if _rc display as error "MISSING_STRESS_TERM=`tag' `term'"
                    else {
                        scalar ese=_se[`term']
                        scalar tt=.
                        scalar pp=.
                        scalar lower=.
                        scalar upper=.
                        if !missing(ese) & ese>0 {
                            scalar tt=eb/ese
                            scalar pp=2*ttail(`df',abs(tt))
                            scalar lower=eb-invttail(`df',.025)*ese
                            scalar upper=eb+invttail(`df',.025)*ese
                        }
                        post coef2 ("`tag'") ("`term'") (eb) (ese) (tt) (pp) (lower) (upper) (`n') (`ng')
                    }
                }
            }
        }
        foreach dropped in CHN USA BOTH {
            local tag "influence_`prefix'_`cutoff'_`dropped'"
            capture noisily estimates use "outputs/stata/`tag'.ster"
            if _rc {
                local missingfits=`missingfits'+1
                display as error "MISSING_INFLUENCE_ESTIMATE=`tag'"
            }
            else {
                local successes=`successes'+1
                local ng=e(N_g)
                local n=e(N)
                local df=e(df_r)
                if missing(`df') | `df'<=0 local df=`ng'-1
                foreach term in L.`outcome' ln_ai_investment ln_ai_patents GDP_Growth {
                    capture scalar eb=_b[`term']
                    if _rc display as error "MISSING_INFLUENCE_TERM=`tag' `term'"
                    else {
                        scalar ese=_se[`term']
                        scalar tt=.
                        scalar pp=.
                        scalar lower=.
                        scalar upper=.
                        if !missing(ese) & ese>0 {
                            scalar tt=eb/ese
                            scalar pp=2*ttail(`df',abs(tt))
                            scalar lower=eb-invttail(`df',.025)*ese
                            scalar upper=eb+invttail(`df',.025)*ese
                        }
                        post coef2 ("`tag'") ("`term'") (eb) (ese) (tt) (pp) (lower) (upper) (`n') (`ng')
                    }
                }
            }
        }
    }
}
postclose coef2
preserve
use "outputs/stata/followup_coefficients.dta", clear
export delimited using "outputs/stata/followup_coefficients.csv", replace
quietly count
display as result "FOLLOWUP_COEFFICIENT_ROWS=" r(N)
restore
display as result "FOLLOWUP_ESTIMATES_OPENED=" `successes' " MISSING=" `missingfits'
log close
if `missingfits' | `successes' != 28 exit 459
