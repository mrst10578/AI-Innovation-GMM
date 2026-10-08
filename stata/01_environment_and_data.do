* Original AI research only; NEVER import datasets from other projects.
version 16.0
capture confirm file "data/processed/stata_ready.dta"
if _rc {
    capture confirm file "data/raw/AI_Balanced_Panel (1).xlsx"
    if _rc {
        display as error "No raw Excel or audited DTA in this folder. Clone repo or download DTA artifact."
        exit 601
    }
    import excel using "data/raw/AI_Balanced_Panel (1).xlsx", firstrow clear
    capture isid ISO3 Year
    if _rc exit 459
    save "data/processed/stata_ready.dta", replace
}
use "data/processed/stata_ready.dta", clear
isid ISO3 Year
assert inrange(Year,2016,2024)
count
display as result "DATA_ROWS=" r(N)
egen panel_id = group(ISO3), label
xtset panel_id Year
assert AI_Investment>=0 if !missing(AI_Investment)
assert AI_Patents>=0 if !missing(AI_Patents)
capture drop ln1p_invest ln1p_patent
gen double ln1p_invest=ln(1+AI_Investment)
gen double ln1p_patent=ln(1+AI_Patents)
capture which xtabond2
if _rc {
    capture noisily ssc install xtabond2
    capture which xtabond2
    if _rc {
        display as error "Cannot install verified SSC xtabond2. Check internet then ssc install xtabond2."
        exit 499
    }
}
display as result "Installed xtabond2:"
which xtabond2
