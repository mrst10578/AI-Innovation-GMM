* AI Innovation GMM reproducibility driver V3: preserve every attempted fit and failure.
* Running this file is not a certificate of econometric validity.
version 16.0
clear all
set more off
capture log close _all
capture mkdir "outputs"
capture mkdir "data/processed"
log using "outputs/stata_preflight.log", text replace
display as result "AI_GMM_FIX_ID=V3_3301_NONMATA_FIRST"
display as text "Stata version " c(stata_version)
display as text "WORKDIR=" c(pwd)
capture noisily do "stata/01_environment_and_data.do"
local pre_rc = _rc
if `pre_rc' {
    display as error "FATAL_PREFLIGHT_RC=" `pre_rc'
    log close
    exit `pre_rc'
}
capture noisily do "stata/02_pre_estimation.do"
local pretests_rc = _rc
if `pretests_rc' display as error "PRETESTS_INCOMPLETE_RC=" `pretests_rc'
log close

* Every model attempted independently. A failed model may not erase its peers.
postfile __audit str22 outcome str4 period str12 method str32 status ///
    str16 engine str244 flags ///
    double rc n groups instruments hdf hp sdf sp ar1p ar2p ///
    double invest_b invest_se patent_b patent_se gdp_b gdp_se ///
    using "outputs/stata_model_summary.dta", replace
local script_failures = 0
foreach outcome in HighTech_Exports Unemployment {
    foreach period in 2024 2023 {
        foreach method in difference system {
            capture noisily do "stata/06_fit_model.do" `outcome' `period' `method'
            local fit_script_rc = _rc
            if `fit_script_rc' {
                local script_failures = `script_failures' + 1
                display as error "MODEL_SCRIPT_FAILED: `outcome' `period' `method' RC=" `fit_script_rc'
                post __audit ("`outcome'") ("`period'") ("`method'") ("SCRIPT_FAILED") ///
                    ("NONE") ("MODEL_SCRIPT_ERROR") ///
                    (`fit_script_rc') (.) (.) (.) (.) (.) (.) (.) (.) (.) ///
                    (.) (.) (.) (.) (.) (.)
            }
        }
    }
}
postclose __audit

preserve
quietly use "outputs/stata_model_summary.dta", clear
quietly count
local model_count = r(N)
quietly count if status == "EXECUTION_FAILED" | status == "SCRIPT_FAILED"
local execution_failures = r(N)
restore

display as result "MODEL_ROWS=" `model_count'
display as result "MODEL_EXECUTION_FAILURES=" `execution_failures'
local failures = `script_failures'
if `model_count' != 8 {
    display as error "INCOMPLETE_MODEL_SUMMARY expected 8 rows, found " `model_count'
    local failures = `failures' + 1
}
capture noisily do "stata/05_post_estimation_and_export.do"
local export_rc = _rc
if `export_rc' local failures = `failures' + 1
if `pretests_rc' {
    display as error "PRETESTS_INCOMPLETE: review outputs/stata_preflight.log"
}
display as result "MODEL_SCRIPT_FAILURES=" `failures'
display as result "MODEL_ESTIMATION_FAILURES=" `execution_failures'
display as text "Results are REVIEW ONLY; see outputs/stata_model_summary.csv and outputs/AI_*.log"
if `failures' | `execution_failures' exit 459
