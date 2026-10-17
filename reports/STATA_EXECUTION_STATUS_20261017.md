**LATER SAME-DAY UPDATE:** The early 'Stata unavailable' status below is superseded. Authentic Stata/MP 17 subsequently ran successfully on Winlator; 16 GMM fits and 64 coefficient rows, full logs and diagnostic exports were saved. [Read the authoritative executed-results report](STATA_REAL_EXECUTION_FINAL_20261017_FA.md). Scientific validation remains pending.

---

# AI investment & patents: actual execution status (2026-10-17)

## What was executed
- Source Excel workbook: **270 observations, 30 ISO3 countries, 2016–2024, fully balanced, 0 missing cells, 0 duplicate keys, no Iran**.
- Observed **5 zero AI investments** and **0 zero patents**; log1p transformations applied only to derived data.
- **26/30** countries report fewer AI patent applications in 2024 than 2023; aggregate patent count rises (938,933 to 1,133,893). This is not evidence of source completeness and could reflect coverage and concentration.
- Generated Stata-format `data/processed/stata_ready.dta` on connected Ubuntu (16 KiB). This is a genuine format conversion, **not** a Stata regression.
- Ran Python audit + **7 pytest tests passed**, and **16 actual R/plm pgmm fits** (2 outcomes × 2 sample end years × 2 equation transformations × 2 step methods), yielding 64 coefficient rows. Logs/CSV and the source-data audit are preserved in `reports/`.
- R 4. and plm 2.6.3 were available on the remote Linux server; see raw execution log for exact R version.

## Example independent R diagnostics: two-step system GMM only

| Response | End year | alpha on lagged response | AR(1) p | AR(2) p | R Sargan p | Instrument columns / groups |
|---|---:|---:|---:|---:|---:|---:|
| HighTech_Exports | 2024 | 0.986 | 0.0375 | 0.2775 | 0.6370 | 16 / 30 |
| HighTech_Exports | 2023 | 0.965 | 0.0164 | 0.7240 | 0.4279 | 15 / 30 |
| Unemployment | 2024 | 1.042 | 0.0213 | 0.9706 | 0.6040 | 16 / 30 |
| Unemployment | 2023 | 1.045 | 0.0124 | 0.6474 | 0.3826 | 15 / 30 |

These are **R output only**, not Stata output and not causal results. Dynamic unemployment coefficients above 1 raise serious persistence/stability concerns. All reported system two-step AI log1p predictor coefficients have p > 0.45 in these fits; that does not establish absence of an effect. The difference-GMM fits have Sargan p values numerically 0 or near 0 and substantial instability; several AR tests are weak, undefined or otherwise concerning (see actual CSV and log). Do not select system GMM solely to pass diagnostic thresholds.

**Critically:** plm's reported `sargan()` is not a defensible substitute for robust Hansen J, and no independently verified difference-in-Hansen subset test is supplied. Source comparability (especially nominal AI investment), the status of 2024 patent reporting, assumed strict exogeneity of GDP growth and system-GMM level moment conditions remain unresolved. Thus *none of these fits is certified as the final professor-ready specification*.

## Stata execution status

| Action | Status |
|---|---|
| Independent model specification and source audit | Prepared / Python tested |
| Data in Stata `.dta` format | Generated on remote Ubuntu; rerunnable in CI |
| Stata `RUN_ALL.do`, data checks and pre-estimation tests | Authored / not yet executed in Stata |
| Stata difference/system GMM; one/two-step; each outcome, full and 2023 sensitivity | Authored / **not yet executed in Stata** |
| Licensed Stata engine on connected Ubuntu or Android | **Unavailable** |
| Actual Stata `.log`, model `.ster`, Hansen/AR(2)/Difference-in-Hansen outputs | **Not produced** |

Use `stata/README_STATA_FA.md` on a device with a licensed Stata executable, then inspect *actual* model logs. Do not copy R coefficients into a file labelled Stata. If Stata fails, retain failure logs and fix code or identification appropriately. Feature work stays on a separate branch pending scientific review.
