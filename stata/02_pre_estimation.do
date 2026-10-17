* Exploratory diagnostics; failure or low power never proves stationarity.
version 16.0
display as text "PRE-ESTIMATION: descriptive statistics"
summarize HighTech_Exports Unemployment GDP_Growth AI_Investment AI_Patents ln_ai_investment ln_ai_patents, detail
pwcorr HighTech_Exports Unemployment GDP_Growth ln_ai_investment ln_ai_patents, sig obs
* Pooled VIF is NOT a within-panel VIF.
regress HighTech_Exports ln_ai_investment ln_ai_patents GDP_Growth i.Year
estat vif
regress Unemployment ln_ai_investment ln_ai_patents GDP_Growth i.Year
estat vif
* T=9: unit-root tests have very limited power; cross-country dependence may invalidate first-generation tests.
foreach v in HighTech_Exports Unemployment ln_ai_investment ln_ai_patents GDP_Growth {
    display as text "IPS unit root test, intercept, 1 ADF lag: `v'"
    capture noisily xtunitroot ips `v', lags(1)
    if _rc display as error "IPS failed for `v' (return code " _rc ")"
    display as text "Fisher ADF unit root test, 1 lag: `v'"
    capture noisily xtunitroot fisher `v', dfuller lags(1)
    if _rc display as error "Fisher failed for `v' (return code " _rc ")"
}
* Pesaran CD only if xtcsd is installed. Missing tool is not a successful test.
capture which xtcsd
if _rc display as text "Pesaran CD NOT RUN: xtcsd unavailable. Do not infer cross-sectional independence."
else {
    capture noisily xtreg HighTech_Exports ln_ai_investment ln_ai_patents GDP_Growth i.Year, fe
    if !_rc {
        capture noisily xtcsd, pesaran abs
        if _rc display as error "Pesaran CD failed for HighTech."
    }
    capture noisily xtreg Unemployment ln_ai_investment ln_ai_patents GDP_Growth i.Year, fe
    if !_rc {
        capture noisily xtcsd, pesaran abs
        if _rc display as error "Pesaran CD failed for Unemployment."
    }
}
