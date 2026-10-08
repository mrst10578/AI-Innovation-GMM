* Independent AI data, no sources from other projects.
version 16.0
capture confirm file "data/processed/stata_ready.dta"
if _rc {
    capture confirm file "data/raw/AI_Balanced_Panel (1).xlsx"
    if _rc exit 601
    import excel using "data/raw/AI_Balanced_Panel (1).xlsx", firstrow clear
    save "data/processed/stata_ready.dta", replace
}
use "data/processed/stata_ready.dta", clear
confirm string variable ISO3
confirm numeric variable Year
foreach v in AI_Investment AI_Patents HighTech_Exports GDP_Growth Unemployment {
    confirm numeric variable `v'
    assert !missing(`v')
}
isid ISO3 Year
assert _N == 270
assert inrange(Year,2016,2024)
assert strlen(ISO3)==3
bysort ISO3: assert _N==9
assert AI_Investment>=0
assert AI_Patents>=0
egen panel_id=group(ISO3), label
xtset panel_id Year
capture drop ln1p_invest ln1p_patent
generate double ln1p_invest=ln(1+AI_Investment)
generate double ln1p_patent=ln(1+AI_Patents)
capture which xtabond2
if _rc {
    capture noisily ssc install xtabond2, replace
    capture which xtabond2
    if _rc {
        display as error "XTABOND2_INSTALL_FAILED: check Stata/SSC network"
        exit 499
    }
}
which xtabond2
