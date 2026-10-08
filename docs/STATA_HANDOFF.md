# Stata handoff: independent AI investment/patents research

**Prepared, NOT run in a licensed Stata executable.** The original workbook already belongs to this repo. Stata model scripts and prerequisites exist on the independent research branch.

## From the repo root on a licensed laptop

1. Ensure data/raw/AI_Balanced_Panel (1).xlsx is present. If a genuine processed DTA Actions artifact is available, put it in data/processed/stata_ready.dta. The preflight can instead import Excel and save the DTA itself.
2. Confirm the working directory is the repository root in Stata, then run:

    ssc install xtabond2, replace
    do "stata/RUN_ALL.do"

3. The driver checks version/runtime, creates outputs/, checks the panel key and transforms log1p, installs/checks SSC xtabond2, runs IPS/Fisher and two separate high-tech exports/unemployment models with difference and system GMM for 2024 and 2023.
4. Read outputs/stata_preflight.log, outputs/stata_hightech_models.log, and outputs/stata_unemployment_models.log. Capture real instrument count, clusters, coefficients, robust Hansen, Sargan, AR(1), AR(2), difference-in-Hansen and any errors. Estimates are saved only if a specific model command completes; files never prove scientific validity on their own.
5. Failure to install xtabond2 or a syntax/runtime error means the affected model is NOT executed and needs documented correction. Do not replace with synthetic logs or invented p-values.

Further Persian explanation: stata/README_STATA_FA.md and DEFENSE_GUIDE_FA.md. R and gretl results can be cross-checked using validation/compare_R_gretl_Stata.py and the actual workflow job artifacts.

This is strictly AI-Innovation-GMM. Do not move data or commands from any other econometrics repository.
