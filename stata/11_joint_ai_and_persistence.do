* Exploratory post-estimation restrictions; no model re-fit and no selection.
* Applies to ALL 16 prespecified stress round 2 saved estimates.
* H0: coefficients on both AI regressors jointly zero.
* H0: autoregressive coefficient equals one. Rejection/non-rejection does not
* by itself establish model identification, causality, or unit-root status.
version 16.0
set more off
cd "D:/AI_Innovation_Stata_Ready"
capture log close _all
log using "outputs/stata/11_joint_ai_and_persistence.log", text replace
postfile wald str32 model double rc joint_ai_p joint_ai_F persistence_equal1_p persistence_equal1_F nobs groups instruments using "outputs/stata/stress_joint_restrictions.dta", replace
local opened=0
local missingfits=0
foreach dep in HighTech_Exports Unemployment {
    local short "hi"
    if "`dep'"=="Unemployment" local short "un"
    foreach cutoff in 2024 2023 {
        foreach spec in D23_X D23_E S23_X S23_E {
            local ident "`short'_`cutoff'_`spec'"
            capture noisily estimates use "outputs/stata/stress_`ident'.ster"
            if _rc {
                local missingfits=`missingfits'+1
                post wald ("`ident'") (601) (.) (.) (.) (.) (.) (.) (.)
                display as error "WALD_MISSING_ESTIMATE `ident'"
            }
            else {
                local opened=`opened'+1
                local n=e(N)
                local ng=e(N_g)
                local k=e(j)
                local jointp=.
                local jointF=.
                local persistp=.
                local persistF=.
                capture noisily test ln_ai_investment ln_ai_patents
                local rcj=_rc
                if !`rcj' {
                    local jointp=r(p)
                    capture local jointF=r(F)
                    if missing(`jointF') capture local jointF=r(chi2)
                }
                capture noisily test L.`dep'=1
                local rcp=_rc
                if !`rcp' {
                    local persistp=r(p)
                    capture local persistF=r(F)
                    if missing(`persistF') capture local persistF=r(chi2)
                }
                post wald ("`ident'") (max(`rcj',`rcp')) (`jointp') (`jointF') (`persistp') (`persistF') (`n') (`ng') (`k')
                display as result "STRESS_WALD=`ident' pAI=`jointp' pLAG_EQ1=`persistp' joint_rc=`rcj' lag_rc=`rcp'"
            }
        }
    }
}
postclose wald
preserve
use "outputs/stata/stress_joint_restrictions.dta", clear
export delimited using "outputs/stata/stress_joint_restrictions.csv", replace
quietly count
display as result "WALD_RECORDS=" r(N)
restore
display as result "WALD_ESTIMATES_OPENED=" `opened' " MISSING=" `missingfits'
log close
if `opened' != 16 exit 459
