# AI Investment & Patents

**One research project per repository.** This repo is dedicated exclusively to high-tech exports and unemployment (30 expected countries, 2016–2024; verify before estimation). It is independent of the other study and of Shakhsi2/3/4.

## Original source package imported from Dropbox

The full ZIP is committed at [research-packages/AI_Research_Ready_Package.zip](research-packages/AI_Research_Ready_Package.zip). All eight source package files have been unpacked. The original Word manuscript, Excel workbook and dictionary, instructor screenshots, extra email note and SHA256 manifest are in [sources/](sources/). The full instruction prompt is in the repository root (MASTER_PROMPT*.md). The workbook is also at [data/raw/AI_Balanced_Panel (1).xlsx](data/raw/) for automated checks.

**Public repository:** these supplied research inputs were explicitly authorized for publication by the user. Do not add personal credentials, hidden API keys, or licensing information.

## Current workflow state

- Python, R/plm and gretl installation/runtime checks were configured separately in GitHub Actions.
- [Validate imported research dataset and build Stata DTA](.github/workflows/05-validate-research-data.yml) checks the real input and creates a `stata_ready.dta` downloadable artifact (if successful).
- The original research data are present; **econometric modeling, IPS/Fisher, GMM, Hansen, Sargan, AR(1)/AR(2), difference-in-Hansen, and genuine Stata estimates are NOT completed**.
- Stata placeholder `stata/02_models.do` intentionally refuses to run until the new chat reviews model assumptions, endogeneity, lags and instruments.

## Tools

Python: `pip install -r requirements-python.txt`. R: `r-base r-cran-plm r-cran-lmtest r-cran-sandwich`; gretl: `gretl`. The GitHub Actions workflows test the tools on Ubuntu without requiring a PC or Android installation.

## Continue in a new chat

Start with [MASTER_PROMPT](./) and the study's `sources/` folder; audit independently, build appropriate estimators, and preserve all unsuccessful and incompatible model specifications in reports. See `docs/STATA_HANDOFF.md`. Never mislabel R/Python results as authentic Stata output.
