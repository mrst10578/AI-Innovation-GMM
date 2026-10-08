# AI-Innovation-GMM scientific status (2026-10-08)

Branch: research/ai-innovation-estimation-20261008.
Draft Pull Request: https://github.com/mrst10578/AI-Innovation-GMM/pull/1 . **DO NOT MERGE without independent audit.**

| Item | Latest evidenced status |
|---|---|
| Original Word, dictionary and Excel audit | Executed in GitHub Actions; 270 rows, 30 countries, 2016-2024, no missing or repeated country-years |
| 2024 patent discrepancy | Executed; 26/30 countries decreased, but total 938933 to 1133893 increased |
| AI source provenance and investment denomination | NOT VERIFIED: exact CSET vintage, dollar magnitude/multiplier and patent reporting lags |
| Python pooled/FE / VIF / graphs / 2023 sensitivity | EXECUTED on real data; observational |
| R plm IPS/Fisher | EXECUTED with p-values; strongly limited by only 9 years |
| R plm pgmm difference/system both outcomes and 2023/2024 | EXECUTED, diagnostics partly reject or invalid (zero df / NaN); NOT uniformly validated |
| gretl pooled/FE/dpanel (v2023c) | EXECUTED, real estimates and nonrobust Sargan logged, validity conditional |
| Cross-engine check | Automated comparison from real R and gretl artifacts; check latest Actions run |
| Stata DO scripts | Prepared for licensed runtime, NOT executed or version-validated |
| Robust Hansen / Difference-in-Hansen | Not independently confirmed; cannot attribute to Stata |
| Iran peer country analysis | NOT performed; need PPP per capita/structure/inflation/digital comparability data |
| Final report / teaching | reports/RESEARCH_REPORT_FA.md and DEFENSE_GUIDE_FA.md delivered; separate PDF produced in conversation |

Commands: python -m src.python.research_audit; python -m src.python.estimate_panel; python -m src.python.prepare_model_data; Rscript src/r/estimate_ai_panel.R; gretlcli -b (absolute script path, CSV absolute inside); python validation/compare_R_gretl_Stata.py after downloading job logs; in licensed Stata, do "stata/RUN_ALL.do" from repo root.

The model is not a validated causal effect. Passing CI is not equivalent to passing identification tests. The public main branch already held original research input; no extra row-level derivatives were committed in this PR.
