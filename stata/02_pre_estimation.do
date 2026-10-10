* Short panel IPS/Fisher are only low-power diagnostics.
version 16.0
xtdescribe
summarize AI_Investment AI_Patents HighTech_Exports GDP_Growth Unemployment, detail
pwcorr ln1p_invest ln1p_patent GDP_Growth HighTech_Exports Unemployment, sig
quietly regress HighTech_Exports ln1p_invest ln1p_patent GDP_Growth
estat vif
foreach v in ln1p_invest ln1p_patent HighTech_Exports Unemployment GDP_Growth {
    display as text "IPS/Fisher, lag0 intercept only, SHORT_T " "`v'"
    capture noisily xtunitroot ips `v', lags(0)
    local ips_rc = _rc
    if `ips_rc' display as error "IPS_FAILED " "`v'" " RC=" `ips_rc'
    capture noisily xtunitroot fisher `v', dfuller lags(0)
    local f_rc = _rc
    if `f_rc' display as error "FISHER_FAILED " "`v'" " RC=" `f_rc'
}
