# Project status (post-Dropbox import)

Project: `AI-Innovation-GMM`. Dataset scope is restricted to this study.

| Phase | Status |
|---|---|
| Independent GitHub code scaffold | Complete on main |
| Dropbox source ZIP uploaded | Complete: `/AI_Research_Ready_Package.zip` |
| Original ZIP imported and SHA256 validated in GitHub Actions | Complete |
| Unpacked Word, Excel, dictionary, screenshots, notes and prompt | Complete in `sources/` and repository root |
| Machine-readable Excel in `data/raw/AI_Balanced_Panel (1).xlsx` | Complete |
| Python / R / gretl environment checks | Previously succeeded |
| Input statistical data audit and DTA export | Github workflow `05-validate-research-data.yml`: check its latest run/artifact |
| Unit roots, correlations/VIF, instrument classification | NOT RUN as final research findings |
| Difference/System GMM and post-estimation tests | NOT RUN |
| Stata 18/xtabond2 | Requires licensed executable and finalized model specification |
| Final paper/report | NOT GENERATED |

Do not treat an installation smoke test, workbook import, or DTA conversion as a statistical estimation. The research manuscript must be studied in full before defining the GMM equations.

## Update 2026-10-17 (isolated feature branch)

- Reviewed original manuscript and dataset; 270 rows, 30 countries, 2016–2024, fully balanced, 0 missing, 0 duplicate, no Iran; 2024 patent decline in 26 countries.
- Authored Stata 01–05 scripts and shared model script; real GMM code replaces previous protective placeholder, but has **not** been executed in licensed Stata.
- Ubuntu source audit + DTA conversion and 7 Python tests succeeded; 16 independent R pgmm fits ran with recorded output and critical validity limitations. See `reports/STATA_EXECUTION_STATUS_20261017.md`.
- Licensed Stata was not present on connected Ubuntu or Android devices; genuine Stata logs, Hansen/AR(2)/difference-in-Hansen status remain pending.
- Branch is intentionally not merged into main until audited run in Stata and scientific review.
