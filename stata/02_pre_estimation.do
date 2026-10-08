* IPS and Fisher with intercept/no trend/lag0: T=9 so low power. Failures are not silently treated as passes.
display as text "VIF on pooled simple explanatory specification"
quietly reg HighTech_Exports ln1p_invest ln1p_patent GDP_Growth
estat vif
pwcorr ln1p_invest ln1p_patent GDP_Growth HighTech_Exports Unemployment, sig
foreach x in ln1p_invest ln1p_patent HighTech_Exports Unemployment GDP_Growth {
    display as text "PANEL_UNIT_ROOT VARIABLE=`x', lag0 intercept, low-power"
    capture noisily xtunitroot ips `x', lags(0)
    if _rc display as error "IPS not available/invalid: `x'"
    capture noisily xtunitroot fisher `x', dfuller lags(0)
    if _rc display as error "Fisher not available/invalid: `x'"
}
