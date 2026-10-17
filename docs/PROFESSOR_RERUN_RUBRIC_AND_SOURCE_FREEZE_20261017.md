# Professor-instructed rerun: source freeze and diagnostic compliance
Date: 2026-10-17

## Correct study history (confirmed with user)

1. Earlier AI-data estimates prepared from preliminary instructor-supplied information were rejected by the professor. The exact substantive reasons for rejection were not preserved in the messages reviewed; **do not attribute the rejection to a specific statistical mistake without evidence**.
2. The current `AI-Innovation-GMM` research panel came from the three attachments forwarded by Bahar in an email dated **2026-09-30, 13:21 +03:30**:
   - `AI_Balanced_Panel (1).xlsx` (email attachment 19,901 bytes)
   - `AI_Balanced_Panel_Dictionary (1).xlsx` (email attachment 6,033 bytes)
   - `بررسی اثرات سرمایه گذاری و ثبت اختراعات هوش مصنوعی بر نرخ اشتغال و نوآوری با فناوری بالا (1).docx` (email attachment 27,735 bytes)
3. Those three filenames and byte sizes match the archived `sources/` copies on the repository checkout. The source workbook in `sources/` and `data/raw/` has identical SHA256 `4f9bf76658d1f495d3eb3e39b226bb5ba6ac39446b35e41bfce4a2aab65d0434`. Direct Gmail attachment download did **not** succeed in this session, so cryptographic identity between mailbox payload and repository remains *unverified*. Do not claim otherwise.
4. In a second Bahar email at 13:37 +03:30, she explicitly notes no Iran observations, asks to consider an Iran-similar group **before** estimation if feasible, otherwise retain all 30 supplied countries.
5. New user screenshots show required pre-estimation and post-estimation diagnostic categories. They are a scientific analysis rubric, not an authorization to discard the supplied dataset.

## Contract for future work

- **The 30-country Excel workbook supplied in the 2026-09-30 email is the analysis sample of record.** Freeze bytes, no additions, no silent WDI/CSET substitutions, no merging with the other Digital-Economy project.
- The later official CSET Country AI Activity reference is an **external provenance comparison only**. A mismatch against another CSET release is not proof the Bahar workbook is incorrect. The workbook can be described accurately as "researcher-supplied curated panel", pending traceability of original CSET fields. If original upstream extraction is unavailable, acknowledge it rather than invent.
- A defensible deliverable must identify actual country/year sample, outcome units, descriptive and diagnostics limitations, all retained failures and robustness checks, actual estimated coefficients, references, and the difference between association and causality.
- Do **not** choose an estimator after seeing its p-values or discard China/USA/2024 just to achieve significance.

## Screenshot-by-screenshot compliance matrix

| Professor's requested item | Existing evidence | Status | Scientific qualification |
| --- | --- | --- | --- |
| IPS panel unit-root tests (`xtunitroot ips`) | 5 original analysis variables in `STATA_REAL_master_20261017.log` | Executed | T=9, limited power; nonstationarity not automatically disqualifying for all dynamic GMM specifications |
| Fisher ADF panel unit-root tests | Same 5 variables in genuine Stata log | Executed | First-generation tests may be affected by cross-sectional dependence |
| Pairwise correlations (`pwcorr`) | Original Stata pre-estimation log | Executed | Descriptive collinearity only |
| VIF after OLS | Two regressions + `estat vif` in original master log; mean VIF 2.04 | Executed | Pooled VIF is not a within/FE multicollinearity test |
| Instruments fewer than countries | 16 baseline and 16 revised GMM diagnostic CSVs; groups=30 and instrument count 10–20 | Executed | Necessary proliferation safeguard, never sufficient for identification |
| Hansen J with robust variance | Printed in genuine `xtabond2, robust small` logs, with revised 16 fits | Executed | Baseline difference GMM has undefined Hansen p-value due to exact identification; revised models now report computable p-values |
| Sargan test | Printed with `xtabond2` | Executed | Sargan is not robust; prioritize carefully interpreted Hansen for robust settings |
| Arellano-Bond AR(1)/AR(2) | Printed for all model runs and CSVs | Executed | Some revised difference-GMM specifications do NOT show a significantly negative AR(1) at 5%; AR(1) heuristic is not a hard theorem |
| Difference-in-Hansen for System GMM subsets | Printed in baseline and revised logs | Executed | Baseline exclusion of level instruments has zero df. Revised system fits report 3–4 df in level-exclusion test, but failure to reject does not prove moment exogeneity |
| Specific instrument-subset tests (`diff` wording in screenshot) | Subset tests already printed by `xtabond2`; `noleveleq` used to fit difference GMM | Implemented by supported estimator mechanisms | Do not assume adding a literal `diff` option is correct or required: validate actual `xtabond2` help before any syntax change |
| Source of AI variables, definitions, version & completeness | Email attachments and curated dictionary; version-to-upstream CSET untraced | **Open** | Must be documented or transparently qualified, not silently replaced |
| Iran-like countries | No Iran in panel; no reproducible pre-estimation comparator rule | **Open** | Use all 30 only with documented inability to define defensible peer subset from supplied data, or seek approval for external peer-descriptor data |
| Final scientific interpretation and professor-ready manuscript | Extended report is exploratory and identifies unstable coefficients | **Open** | Results must be reported as tentative without claiming proven effects; revise title/proxies and confirm theoretical justification |

## Scientific observations from completed reruns

- 16 baseline GMM fits and 16 pre-registered expanded-lag/exogeneity stress fits, plus 12 China/USA exclusions, completed in real Stata. 44 estimates, 176 exported coefficient records. Ten Python quality tests passed.
- Baseline GMM produced moment-covariance singularity warnings; no such warning was recorded in the 16 expanded-lag sensitivity runs, whereas the 12 influence reruns of the *original* model retained the warnings.
- The 16 revised runs have computable Hansen values and printed Difference-in-Hansen subsets; nothing establishes causal instrument exogeneity conclusively.
- Both joint AI coefficients were jointly not significant at 5% in all 16 revised fits; lagged-outcome coefficient equals one was not rejected at 5%. That is *lack of evidence under these designs*, not evidence of zero effects or a unit root.
- The original 2024 patent series is extremely concentrated in China (92.07% of sample total), US AI investment (nominal record) is 71.52% of sample. Source and interpretation need review.

## Exact next development priorities

1. Map each hypothesis from the supplied research DOCX to actual proxies and units; revise misleading language such as "employment" vs unemployment and "innovation" vs high-tech export share, and coefficient descriptions.
2. Generate compact, readable **professor-specified diagnostic tables** from the actual Stata CSV/logs, including numeric unit-root test stats, VIF, instrument N/groups, AR1/AR2, Hansen/Sargan and level-subset Difference-in-Hansen; mark missing/non-testable entries, no fabricated values.
3. Document the Iran-peers feasibility decision and why no Iranian observations exist.
4. Perform one independent, theory-appropriate model review / alternative associative panel estimator, separately from GMM, without changing the source workbook.
5. Produce a conditional professor-facing manuscript and reproducibility package; subject it to scientific and visual proofreading. If source/identification issues cannot be resolved, label conclusions exploratory rather than promising causal certainty.

**Current submission verdict:** Computational compliance with screenshots largely complete. Scientific completeness, interpretation and data lineage remain open. Do not claim the previously rejected version is redeemed merely because tests execute.
