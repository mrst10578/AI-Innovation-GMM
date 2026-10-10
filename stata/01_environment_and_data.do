* Always re-import the ORIGINAL, audited workbook to prevent stale DTA reuse.
* Provenance of upstream CSET/WDI series remains UNVERIFIED.
version 16.0
capture confirm file "data/raw/AI_Balanced_Panel (1).xlsx"
if _rc {
    display as error "MISSING_ORIGINAL_WORKBOOK"
    exit 601
}
import excel using "data/raw/AI_Balanced_Panel (1).xlsx", firstrow clear
confirm string variable ISO3
confirm numeric variable Year
foreach v in AI_Investment AI_Patents HighTech_Exports GDP_Growth Unemployment {
    confirm numeric variable `v'
    assert !missing(`v')
}
isid ISO3 Year
assert _N == 270
assert inrange(Year, 2016, 2024)
assert strlen(ISO3) == 3
bysort ISO3: assert _N == 9
assert AI_Investment >= 0
assert AI_Patents >= 0
assert inrange(HighTech_Exports, 0, 100)
assert inrange(Unemployment, 0, 100)
sort ISO3 Year
save "data/processed/stata_ready.dta", replace
egen panel_id = group(ISO3), label
xtset panel_id Year
generate double ln1p_invest = ln(1+AI_Investment)
generate double ln1p_patent = ln(1+AI_Patents)
count
display as result "ORIGINAL_WORKBOOK_IMPORTED_ROWS=" r(N)
capture which xtabond2
if _rc {
    capture noisily ssc install xtabond2
    capture which xtabond2
    if _rc {
        display as error "XTABOND2_NOT_INSTALLED: Stata SSC network access required"
        exit 499
    }
}
which xtabond2
capture noisily xtabond2, version
display as text "PACKAGE_VERSION_CHECK_RC=" _rc
display as text "UPSTREAM_SOURCE_VERSION_NOT_VERIFIED"
