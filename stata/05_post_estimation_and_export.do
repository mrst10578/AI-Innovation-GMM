* Model-specific logs and .ster files are saved by _run_one_model.do.
* Post-estimation diagnostics printed by xtabond2 must be inspected per specification.
* Do not treat statistical insignificance of AR(2) or Hansen alone as proof of validity.
display as text "OUTPUT: outputs/stata/hightech.log and outputs/stata/unemployment.log"
display as text "GMM status remains REVIEW_PENDING until instrument count < groups,"
display as text "AR(2) and overidentification diagnostics are examined, and missing tests documented."
display as text "Difference-in-Hansen is available only if reported for appropriate nested instrument subsets."
display as text "Sensitivity: 2016-2023 is separately stored; do not silently discard 2024."
