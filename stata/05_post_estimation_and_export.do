* Exports: the original xtabond2 output already includes Hansen/Sargan and AB tests.
* Difference-in-Hansen is automatic for eligible system models (gmmstyle split).
* Do not invent unavailable returned scalars or degrees of freedom.
display as text "POST_ESTIMATION: examine actual Stata log of each model; record test statistics and df."
display as text "If Hansen rejects, AR(2) rejects or instrument count >= N, classify model unvalidated."
display as text "Save Stata textual logs and .ster estimates; do not claim Stata results before licensed run."
