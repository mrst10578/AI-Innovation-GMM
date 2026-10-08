* Model A, technology exports SHARE in percentage points, not patent/innovation count.
version 16.0
capture log close _all
log using "outputs/stata_hightech_models.log", text replace
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
    display as text "HIGH_TECH period end `ending' dynamic Difference GMM"
    capture noisily xtabond2 HighTech_Exports L.HighTech_Exports ln1p_invest ln1p_patent GDP_Growth `timedummies', ///
        gmmstyle(L.HighTech_Exports, lag(1 2) collapse) ///
        gmmstyle(ln1p_invest ln1p_patent GDP_Growth, lag(2 3) collapse) ///
        ivstyle(`timedummies', equation(diff)) noleveleq twostep robust small
    if _rc display as error "Difference GMM failed for HighTech `ending'; not a valid estimate."
    else estimates save "outputs/stata_hightech_diff_`ending'.ster", replace
    display as text "HIGH_TECH period end `ending' dynamic System GMM"
    capture noisily xtabond2 HighTech_Exports L.HighTech_Exports ln1p_invest ln1p_patent GDP_Growth `timedummies', ///
        gmmstyle(L.HighTech_Exports, lag(1 2) collapse split) ///
        gmmstyle(ln1p_invest ln1p_patent GDP_Growth, lag(2 3) collapse) ///
        ivstyle(`timedummies') twostep robust small
    if _rc display as error "System GMM failed for HighTech `ending'; not a valid estimate."
    else {
        estimates save "outputs/stata_hightech_sys_`ending'.ster", replace
        ereturn list
        display as text "VALIDATE instrument count, Hansen, AR(1)/AR(2), difference-in-Hansen in printed log."
    }
    restore
}
log close
