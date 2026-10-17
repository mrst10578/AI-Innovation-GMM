# Prespecified high-concentration leave-country-out tests (2026-10-17)

This document is committed before running the 12 fits.

The original 2024 panel has a **92.0746%** China share of AI patents and a **71.5241%** US share of nominal AI investment (arithmetic from the original Excel). Among 30 countries, **26 countries decreased** AI patent counts in 2024 versus 2023, but China's count increased by 260,214 and total patent applications rose by 194,960. Hence the aggregate trend is dominated by China. This observation alone does **not** establish source incompleteness, though the coverage and aggregation choices must be independently checked.

**Analysis precommitment:** For each of the two dependent variables and both sample endpoints (2016–2024 / 2016–2023), rerun the **original one-to-one comparable two-step system GMM** (not a selectively optimized version) on the following three samples:
- exclude China (CHN),
- exclude the USA,
- exclude both China and the USA.

Do not silently replace a dropped country. For each of 12 runs record country count, observation count, instruments, AR1/AR2, Sargan/Hansen, lagged-outcome coefficient, AI investment coefficient, AI patents coefficient, GDP coefficient, and full printed Difference-in-Hansen and rank warning messages.

The 4 full-sample counterparts already exist in `reports/STATA_REAL_gmm_diagnostics_20261017.csv` and `reports/STATA_REAL_coefficients_20261017.csv`; they should not be re-estimated with different settings just to compare. Keep source data unchanged. A model with a good diagnostic p-value but unsupported moments remains on scientific hold.

**Critical caveat:** This is an influence/sensitivity analysis, not a cure for concentrated source measurement, omitted variables, small T, or the system-GMM level-moment assumptions.
