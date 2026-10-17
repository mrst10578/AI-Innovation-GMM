* Export exact numeric coefficients from actual Stata .ster files only.
* Independent AI Investment/Patents panel. Run after RUN_ALL.do.
version 16.0
set more off
cd "D:/AI_Innovation_Stata_Ready"
capture log close _all
log using "outputs/stata/06_stata_coefficient_export.log", text replace
postfile ai_coef str36 model str36 term double b robust_se t_stat p_value ci_low ci_high using "outputs/stata/stata_coefficients.dta", replace
local successes 0
local missing_models 0
foreach outcome in hi un {
    foreach endyear in 2024 2023 {
        foreach equation in system difference {
            foreach step in onestep twostep {
                local model "`outcome'_`equation'_`step'_`endyear'"
                capture noisily estimates use "outputs/stata/`model'.ster"
                if _rc {
                    local missing_models = `missing_models' + 1
                    display as error "MISSING_STATA_ESTIMATE=`model'"
                }
                else {
                    local successes = `successes' + 1
                    local dep "HighTech_Exports"
                    if "`outcome'"=="un" local dep "Unemployment"
                    local dof = e(df_r)
                    if missing(`dof') | `dof'<=0 local dof=e(N_g)-1
                    foreach term in L.`dep' ln_ai_investment ln_ai_patents GDP_Growth {
                        capture scalar coeff = _b[`term']
                        if _rc {
                            display as error "MISSING_COEFFICIENT model=`model' term=`term'"
                        }
                        else {
                            scalar sigma = _se[`term']
                            scalar tvalue = .
                            scalar pvalue = .
                            scalar lo = .
                            scalar hi = .
                            if !missing(sigma) & sigma>0 {
                                scalar tvalue = coeff/sigma
                                scalar pvalue = 2*ttail(`dof',abs(tvalue))
                                scalar lo = coeff-invttail(`dof',.025)*sigma
                                scalar hi = coeff+invttail(`dof',.025)*sigma
                            }
                            post ai_coef ("`model'") ("`term'") (coeff) (sigma) (tvalue) (pvalue) (lo) (hi)
                            display as text "COEFFICIENT_RECORDED model=`model' term=`term' b=" coeff " se=" sigma
                        }
                    }
                }
            }
        }
    }
}
postclose ai_coef
preserve
use "outputs/stata/stata_coefficients.dta", clear
export delimited using "outputs/stata/stata_coefficients.csv", replace
quietly count
display as result "ACTUAL_STATA_COEFFICIENT_ROWS=" r(N)
restore
display as result "STATA_ESTIMATES_OPENED=`successes'"
display as result "STATA_ESTIMATES_MISSING=`missing_models'"
log close
