* Always derive analysis data from the original instructor-supplied Excel.
* NEVER trust a cached processed .dta when source Excel exists.
version 16.0
set more off
capture confirm file "data/raw/AI_Balanced_Panel (1).xlsx"
if _rc {
    display as error "Original instructor-provided Excel not found: refusing stale .dta fallback."
    exit 601
}
capture noisily import excel using "data/raw/AI_Balanced_Panel (1).xlsx", sheet("Sheet1") firstrow clear
local import_rc = _rc
if `import_rc' {
    display as error "Stata import from original Excel failed, rc=`import_rc'"
    exit `import_rc'
}
foreach v in ISO3 Year AI_Investment AI_Patents HighTech_Exports GDP_Growth Unemployment {
    capture confirm variable `v'
    if _rc {
        display as error "Original supplied Excel lacks required variable `v'"
        exit 111
    }
}
isid ISO3 Year
assert inrange(Year,2016,2024)
assert !missing(ISO3,Year,AI_Investment,AI_Patents,HighTech_Exports,GDP_Growth,Unemployment)
assert AI_Investment >= 0 & AI_Patents >= 0
assert HighTech_Exports > 0
assert inrange(Unemployment,0,100)
encode ISO3, gen(panel_id)
xtset panel_id Year
bysort panel_id (Year): assert _N == 9
egen tag_country = tag(panel_id)
quietly count if tag_country
assert r(N) == 30
assert _N == 270
drop tag_country
gen double ln_ai_investment = ln(1 + AI_Investment)
gen double ln_ai_patents = ln(1 + AI_Patents)
label variable ln_ai_investment "ln(1 + instructor-supplied nominal AI investment)"
label variable ln_ai_patents "ln(1 + instructor-supplied AI patent applications)"
forvalues yy=2017/2024 {
    gen byte yr`yy' = Year == `yy'
}
capture mkdir "data"
capture mkdir "data/processed"
capture noisily save "data/processed/stata_ready.dta", replace
local save_rc = _rc
if `save_rc' {
    display as error "Validated source loaded; could not save derivative Stata data, rc=`save_rc'"
    exit `save_rc'
}
display as result "ORIGINAL_INSTRUCTOR_EXCEL_REIMPORTED_AND_VALIDATED=1"
display as result "SOURCE_AUDIT_PASS=1 COUNTRIES=30 YEARS=9 ROWS=270 IMPUTED=0"
tab Year
xtdescribe
