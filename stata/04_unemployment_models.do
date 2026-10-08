* Model B, unemployment percentage of labor force (NOT employment percentage).
version 16.0
capture log close _all
log using "outputs/stata_unemployment_models.log", text replace
do "stata/01_environment_and_data.do"
foreach ending in 2024 2023 {
    preserve
    keep if Year<=`ending'
    capture drop yrd_*
    quietly tab Year, gen(yrd_)
    local timedummies
    foreach var of varlist yrd_* {
        if "`var'" != "yrd_1" local timedummies "`timedummies' `var'"
    }
    display as text "UNEMPLOYMENT period end `ending' dynamic Difference GMM"
    capture noisily xtabond2 Unemployment L.Unemployment ln1p_invest ln1p_patent GDP_Growth `timedummies', ///
        gmmstyle(L.Unemployment, lag(1 2) collapse) ///
        gmmstyle(ln1p_invest ln1p_patent GDP_Growth, lag(2 3) collapse) ///
        ivstyle(`timedummies', equation(level)) noleveleq twostep robust small
    if _rc display as error "Difference GMM failed for unemployment `ending'; not a valid estimate."
    else estimates save "outputs/stata_unemployment_diff_`ending'.ster", replace
    display as text "UNEMPLOYMENT period end `ending' dynamic System GMM"
    capture noisily xtabond2 Unemployment L.Unemployment ln1p_invest ln1p_patent GDP_Growth `timedummies', ///
        gmmstyle(L.Unemployment, lag(1 2) collapse split) ///
        gmmstyle(ln1p_invest ln1p_patent GDP_Growth, lag(2 3) collapse) ///
        ivstyle(`timedummies', equation(level)) twostep robust small
    if _rc display as error "System GMM failed for unemployment `ending'; not a valid estimate."
    else {
        estimates save "outputs/stata_unemployment_sys_`ending'.ster", replace
        ereturn list
        display as text "VALIDATE instrument count, Hansen, AR(1)/AR(2), difference-in-Hansen in printed log."
    }
    restore
}
log close
