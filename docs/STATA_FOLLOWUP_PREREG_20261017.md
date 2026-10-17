# Pre-registered second Stata diagnostic round (2026-10-17)

This file was committed **before** the diagnostic follow-up fits. Do not select a preferred model according to p-values.

## Why a second round?

The first real run of 16 dynamic models is archived in `reports/STATA_REAL_*`. All eight difference-GMM variants used the same number of instruments as freely estimated coefficients and yielded `Hansen chi2(0)`: this is **exact identification and does not test instrument validity**. All models emitted singular-moment covariance warnings, sometimes with generalized inverses. System-GMM estimates use extra level moments that cannot be proven valid from lack of rejection. Small N=30, T=9 and collinear time indicators compound concerns.

## Four fixed-before-running sensitivity specifications

For **each** outcome (HighTech_Exports / Unemployment) and cutoff (2024 / 2023), estimate exactly four **two-step robust small** collapsed GMM specifications:

1. **D23_X**: Difference GMM, treat lagged outcome as endogenous with instruments `gmmstyle(L.y,lag(1 2) collapse)`, current AI investment and AI patents with `gmmstyle(AI,lag(2 3) collapse)`, GDP growth provisionally strictly exogenous, and 2018+ calendar dummies as standard IV.
2. **D23_E**: Same as D23_X, but treat GDP growth as endogenous with collapsed lags 2 to 3 and remove GDP from standard IV.
3. **S23_X**: System GMM with the same expanded lagged-outcome/AI instruments as D23_X, GDP and calendar dummies as standard IV in both equations.
4. **S23_E**: System GMM as D23_E with endogenous GDP-growth instruments; only calendar dummies as standard IV in both equations.

All models use `yr2018-yr2024` (or through 2023), not the earlier redundant `yr2017` dummy; 2017 precedes the first dynamic usable periods. This explicitly tests whether a redundant calendar instrument contributes to rank deficiency. The narrow additional lag window `[1,2]` for **L.Y** corresponds to original Y dated at least `t-2`, while current AI and GDP (when endogenous) use `[2,3]` (`t-2,t-3`); this is a sensitivity check, **not** validation of instrument exogeneity or relevance.

**16 combinations total.** Log every fit and failure. Preserve instruments/groups, Hansen, Sargan, AR(1), AR(2), autoregressive persistence, all key AI coefficients and robust SE. Explicitly preserve any singular covariance warnings and any Difference-in-Hansen failures. Do not suppress missing values as zero.

## Additional source audit

Calculate country-level patent and investment totals 2023/2024, identify contributions to aggregate 2024 change and concentration. Differences in patent coverage/collection may be the cause; do not state this as fact without provider revision metadata. Original workbook must remain byte-for-byte unchanged.

## Acceptance criteria

No instrument count >= group count; first-step rank and GMM moment covariance must be non-singular or diagnosed; AR(2) and Hansen must be interpretable (positive overidentification df). Check level subset difference-in-Hansen with non-zero residual df. Require stability of persistence and coefficients and discuss small-sample standard error risks. Passing test thresholds **does not imply causal identification**. A model that cannot satisfy defensible moment assumptions remains on scientific hold; no cherry-picking or silently removing 2024.

Only genuine Stata logs and CSVs may be labelled 'Stata'. If the GUI disconnects, no estimated results will be asserted until real outputs are observed.
