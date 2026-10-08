# MODEL SPECIFICATION | AI investment and patents (independent)

## Provenance and confirmed dataset
- 2026-10-08: original `sources/` manuscript and dictionary inspected by GitHub Actions.
- `data/raw/AI_Balanced_Panel (1).xlsx`: 270 complete observations, 30 ISO3 countries, 2016–2024, no duplicates, no missing cells in seven columns.
- Iran is **not** one of the 30 countries.
- Main dependent variable A: `HighTech_Exports` = WDI `TX.VAL.TECH.MF.ZS`, share of manufactured exports measured in percentage points, NOT export revenue and NOT a direct innovation count.
- Main dependent variable B: `Unemployment` = WDI `SL.UEM.TOTL.ZS`, percent labor force, NOT employment rate.
- `GDP_Growth` = WDI `NY.GDP.MKTP.KD.ZG`, real annual GDP growth in percentage points.
- `AI_Investment`: dictionary says nominal investment **often** in USD; exact amount multiplier (USD, thousand or millions), vintage, and coverage **not independently verified**. Cannot assert real dollars or broad capital spending. `AI_Patents`: source says number of *applications*, but exact source vintage and application/publication lag unverified.
- CSET CAT describes investment as Crunchbase-derived equity transactions in private firms and patents from unified patent datasets. This documents the **general CSET methodology**, not proof of exact workbook extract/provenance. Source: https://cat.cset.tech/methodology/ ; https://cat.eto.tech/ . WDI indicator metadata: https://databank.worldbank.org/metadataglossary/world-development-indicators/series/TX.VAL.TECH.MF.ZS .
- Original manuscript's proposed interpretation of both AI log coefficients as pure elasticities is too broad: `ln(1+x)` and unlogged percentage-point outcomes do not imply constant elasticities.

## Estimands and transformations
For `Y ∈ {HighTech_Exports, Unemployment}`:

`Y_it = alpha Y_i,t-1 + beta1 ln(1+AI_Investment_it) + beta2 ln(1+AI_Patents_it) + gamma GDP_Growth_it + mu_i + lambda_t + e_it.`

- Outcomes are estimated in their source percentage-point levels.
- Five exact zeros for `AI_Investment`; no zeros in `AI_Patents`. Negative GDP growth remains in levels (never log-transformed).
- Outcomes' 1-year persistence is modeled explicitly.
- Common shocks controlled via year effects; unobserved country effects via country fixed effects/differencing.
- The two AI variables and the lagged outcome are provisionally endogenous. GDP growth is *not* assumed strictly exogenous: treat as potentially predetermined/endogenous and use constrained lagged instruments. These are methodological hypotheses, **not validated identification**.
- Collapsed internal GMM-style instruments with dependent outcome/AI/GDP lags 2:3, and sensitivity to just lag 2. The R pgmm formula, gretl dpanel, and Stata xtabond2 syntax use different conventions; compare their **effective** periods, instrument matrices, and moment assumptions, never merely identical lag option strings.
- Difference GMM first; System GMM only conditional on additional level-equation moment restrictions; one-step with robust standard errors where supported. No pretense that `pgmm` or gretl precisely reproduce Stata's Windmeijer two-step or Difference-in-Hansen.
- Counts of instruments must remain substantially below 30 country clusters. Higher instrument counts, AR(2) rejection, near-singular estimates or unsupported extra level restrictions **disqualify interpretation as validated GMM**.

## 2024 preregistered sensitivity and sources
- Full 2016–2024 panel compared with 2016–2023. Exclude 2024 ONLY as an explicitly flagged robustness exercise, not for statistical significance.
- The original data show 26/30 countries with fewer AI patent applications in 2024 vs 2023, yet summed patents increase from 938,933 to 1,133,893; inspect extreme country influence and extraction vintages. A 2024 reporting-lag mechanism remains **hypothesis**, not a verified error.
- CSET time stamps/data revisions and indicators need row-level side-by-side reconciliation before causal claims.
- Iran peer-country sample cannot be selected using only AI panel values: must externally validate GDP PPP per capita, inflation, digital sector, production structure and a pre-specified similarity metric. Do not automatically fit large-N GMM on tiny peer subsets.

## Status gates
1. Source inspection: executed, original data integrity confirmed.
2. Python descriptive/pooled/FE and 2024 sensitivity: see live Actions logs; historical status not imputed.
3. R IPS/Fisher and pgmm: provisional, inspect live logs and instrument counts.
4. gretl dpanel: independently attempted, inspect live logs and flags.
5. Stata xtabond2/Hansen AR(1)/AR(2)/Difference-in-Hansen: **not executed** without licensed Stata. Do not report Stata statistics.
6. Structural causal claims: **not established**; observational research until source and moments fully audited.
