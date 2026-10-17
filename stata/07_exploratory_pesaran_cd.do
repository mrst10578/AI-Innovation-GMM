* Exploratory Pesaran (2004) CD calculated on static FE residuals.
* Uses only official Stata commands; does not misrepresent this as xtcsd output.
* T=8/9 after excluding 2024; time dummies imply caution in null approximation.
version 16.0
set more off
cd "D:/AI_Innovation_Stata_Ready"
capture log close _all
log using "outputs/stata/07_exploratory_pesaran_cd.log", text replace
do "stata/01_environment_and_data.do"
postfile cd_post str20 outcome double end_year years groups pairs avg_pair_rho cd_stat p_value using "outputs/stata/exploratory_cd.dta", replace
foreach y in HighTech_Exports Unemployment {
    foreach cutoff in 2024 2023 {
        capture noisily xtreg `y' ln_ai_investment ln_ai_patents GDP_Growth i.Year if Year<=`cutoff', fe
        if _rc {
            display as error "FE_FOR_CD_FAILED `y' cutoff=`cutoff' rc=" _rc
        }
        else {
            tempvar res
            predict double `res' if e(sample), e
            preserve
            keep if !missing(`res')
            keep Year panel_id `res'
            rename `res' eps
            quietly reshape wide eps, i(Year) j(panel_id)
            local N 30
            local T = _N
            scalar sumrho = 0
            local pairs = 0
            forvalues i=1/29 {
                local jstart = `i'+1
                forvalues j=`jstart'/30 {
                    quietly correlate eps`i' eps`j'
                    matrix CDcorr = r(C)
                    scalar corr_ij = CDcorr[1,2]
                    if !missing(corr_ij) {
                        scalar sumrho = sumrho + corr_ij
                        local pairs = `pairs' + 1
                    }
                }
            }
            if `pairs' != 435 {
                display as error "CD_REQUIRES_ALL_435_PAIRS; got `pairs'"
                post cd_post ("`y'") (`cutoff') (`T') (`N') (`pairs') (.) (.) (.)
            }
            else {
                scalar avg_rho = sumrho/`pairs'
                scalar cd_stat = sqrt(2*`T'/(`N'*(`N'-1)))*sumrho
                scalar cd_p = 2*normal(-abs(cd_stat))
                display as result "EXPLORATORY_CD outcome=`y' cutoff=`cutoff' T=`T' groups=`N' pairs=`pairs' avg_rho=" avg_rho " CD=" cd_stat " normal_approx_p=" cd_p
                post cd_post ("`y'") (`cutoff') (`T') (`N') (`pairs') (avg_rho) (cd_stat) (cd_p)
            }
            restore
        }
    }
}
postclose cd_post
preserve
use "outputs/stata/exploratory_cd.dta", clear
export delimited using "outputs/stata/exploratory_cd.csv", replace
quietly count
display as result "CD_RECORDS=" r(N)
restore
display as text "CAUTION: descriptive static FE residual CD under short T and estimated year effects."
display as text "This is NOT the xtcsd package or CD test of GMM residuals."
log close
