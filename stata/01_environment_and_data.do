* Read unmodified data; validate panel; create analysis variables.
version 16.0
set more off
capture confirm file "data/processed/stata_ready.dta"
if _rc {
    display as error "DTA missing. From repo root run: python -m src.python.to_stata"
    exit 601
}
use "data/processed/stata_ready.dta", clear
foreach v in ISO3 Year AI_Investment AI_Patents HighTech_Exports GDP_Growth Unemployment {
    capture confirm variable `v'
    if _rc {
        display as error "Missing required column: `v'"
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
label variable ln_ai_investment "ln(1 + recorded nominal AI investment)"
label variable ln_ai_patents "ln(1 + recorded AI patent applications)"
forvalues yy=2017/2024 {
    gen byte yr`yy' = Year == `yy'
}
display as result "SOURCE AUDIT PASS: 30 countries, 270 rows, 2016-2024. No imputation."
tab Year
xtdescribe
