# Audited model specification (2026-10-17)

**Scope:** This file is exclusively for the AI investment/patents project, not the digital-economy study.

## Provenance and measurement
The original supplied workbook has 270 complete observations, 30 countries, years 2016–2024, unique ISO3-Year keys and no Iran. Original inputs remain unchanged. According to the supplied dictionary, `HighTech_Exports` is **percentage of manufacturing exports**, not the number of innovations; `Unemployment` is **unemployment rate**, not employment rate. `AI_Investment` units are described imprecisely as nominal value, often USD, and the CSET aggregation/coverage is not independently verified. `AI_Patents` counts applications, not necessarily granted patents. No causal interpretation is justified by the current evidence.

The correct transformations are `ln_ai_investment=ln(1+AI_Investment)` and `ln_ai_patents=ln(1+AI_Patents)`. The five zero investments require log1p; elasticities are not constant near zero. GDP_Growth and the two outcomes remain in percentage points. AI patent counts in 2024 are below 2023 in **26/30** countries despite the higher aggregate total, a source-completeness warning requiring sensitivity checks. No Iran peer group is created: the workbook lacks Iran and independent covariates for ex-ante matching.

## Provisional estimands
Separate equations, for `Y=HighTech_Exports` and `Y=Unemployment`:

`Y_it = alpha * Y_i,t-1 + beta1 * ln(1+AI_Investment_it) + beta2 * ln(1+AI_Patents_it) + gamma * GDP_Growth_it + country_FE_i + year_FE_t + eps_it.`

- Country fixed effects are eliminated in the difference equation and handled through GMM moment assumptions in the system equation.
- Year indicators: 2017–2024 (2016 base), reduced to 2017–2023 in the sensitivity sample.
- Dynamic pooled OLS and within-FE (cluster-robust by country) are **biased comparison specifications**, not causal estimates.
- Endogeneity: lagged response and contemporary AI variables are instrumented as potentially endogenous. For `L.Y`, collapsed lag 1 of the lagged variable corresponds to **Y dated t-2**; for contemporary AI variables, use collapsed lag 2. This is deliberately narrow to keep the instrument matrix small.
- GDP growth and time dummies are treated as strictly exogenous **only provisionally**, a particularly contestable assumption for GDP growth. Alternative classifications should be checked before claiming causal conclusions.
- Run one- and two-step collapsed difference and system GMM, `robust small`, separately for 2016–2024 and 2016–2023. Assess one-step as an additional robustness check.
- System GMM adds level moment conditions requiring mean-stationarity-style restrictions. These are **assumptions to interrogate**, not guaranteed by a balanced panel.
- With only 30 groups and 8–9 years, system GMM may be weak, overfit, or unidentified even when estimable. The code does **not** automatically declare fits valid.
- After *actual licensed Stata execution*, check instrument count relative to 30 groups, AR(1), AR(2), Hansen J, Sargan, and Difference-in-Hansen for valid subsets if available. Nonrejection of any null does **not** establish instrument validity. Record absence of diagnostics rather than filling missing cells.
- IPS and Fisher ADF tests are exploratory only: with T=9 they have poor power and may be invalid under cross-sectional dependence; Pesaran CD is attempted only if `xtcsd` is installed. Pooled VIF does not equal within-panel VIF.
- **2024 sensitivity** is precommitted: analyze with and without 2024, do not pick a window according to coefficient significance.

## Status and reproducibility
These scripts are **prepared for Stata** but are not Stata results until a licensed Stata binary runs them and writes real logs. Currently connected Ubuntu/Android endpoints do not expose a Stata binary. No GMM significance or diagnostic p-values are asserted in this file. Inspect the `.ster` estimates and each model log after running; failed models remain failed, without substitution.
