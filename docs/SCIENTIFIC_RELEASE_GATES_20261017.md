# SCIENTIFIC RELEASE GATES: HOLD / NOT PROFESSOR-READY
Date: 2026-10-17

## Independent World Bank source check (same day update)

An additional **read-only comparison of all 810 supplied country-year values** with live official World Bank API series was performed. The API reported source update `2026-10-08`, **after** the 2026-09-30 Bahar email. The untouched supplied panel has:
- `GDP_Growth` / NY.GDP.MKTP.KD.ZG: **270/270** within absolute 0.001
- `Unemployment` / SL.UEM.TOTL.ZS: **270/270** within absolute 0.001
- `HighTech_Exports` / TX.VAL.TECH.MF.ZS: **253/270** within absolute 0.001; **17 mismatches**, largest France 2020 difference 1.3482 percentage points

Reproducible independent script: `src/python/verify_wdi_reference.py`. Frozen 810-row detailed audit: `reports/WDI_REFERENCE_ROW_COMPARISON_20261017.csv`; metadata and 17 discrepancy records: `reports/WDI_REFERENCE_RECONCILIATION_20261017.json`. Two additional Python tests make **12 passing offline quality tests**. These findings substantiate the provenance of the 3 World Bank fields far more strongly than before, but **do not prove the cause of 17 revision differences**, and **do not resolve upstream version/field/units for the two AI series**. Never silently overwrite the original workbook.

The Mikhak PDF/DOCX review now includes these findings and an all-17 discrepancies appendix. **68 authentic Stata fitted comparisons** are archived (44 GMM and 24 FE/OLS benchmarks); this number does not imply scientific identifiability. The remaining blocked release gates are mainly raw AI-series provenance and credible identification.

---

## Executive decision

**NO-GO for final scientific submission** at this stage. Real Stata execution and QA are successful, but those technical results cannot establish source provenance or credible causal identification. A scientific manuscript cannot honestly be called "flawless"; the target is fully disclosed methods, verifiable source lineage, reproducible code and defensible conclusions.

### What has been completed

- 30-country, 270-row supplied panel preserved with original workbook SHA256 `4f9bf76658d1f495d3eb3e39b226bb5ba6ac39446b35e41bfce4a2aab65d0434`.
- 44 successful real Stata GMM fits (16 baseline, 16 prespecified lag/GDP classifications, 12 CHN/USA leave-out), 176 individual coefficient/SE/CI rows and 16 post-fit joint hypothesis/persistence tests.
- Revised lag window eliminated the previously printed singular moment-covariance warnings, and restored positive overidentification degrees of freedom, but this does NOT prove instrument validity.
- 12 Python data/evidence consistency tests passed; raw Stata and independent R outputs labelled separately. PR #2 remains draft/unmerged.

## Gate 1. Original data provenance: BLOCKED (highest priority)

The supplied dictionary says "CSET" generically for `AI_Patents` and `AI_Investment`, but contains no exact version, raw field name, indicator construction, export date, or calculation code. The official CSET/ETO Country AI Activity Metrics **release 1.11.0, published 2026-03-19**, is available at:

- Dataset release: https://zenodo.org/records/19103157
- Official definitions: https://eto.tech/dataset-docs/country-ai-activity-metrics/index.html
- Original-vs-official comparison from a verified, CRC-checked `cat.zip` with SHA256 `ce36ddfddf511caa92ac845ccf5663233158945acfb31446195e1ba4088b192f`: `reports/CSET_REFERENCE_COMPARISON_20261017.json`
- Reproducible read-only comparison code: `src/python/verify_cset_reference.py`

| Country | Year | Supplied AI patents | CSET v1.11.0 "All" AI patent applications | Official patent record complete? | Supplied AI investment | Official 2026 estimated investment | Official 2026 disclosed investment |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| CHN | 2023 | 783813 | 120006 | no | 17598 | 10593 | 5294 |
| CHN | 2024 | 1044027 | 131117 | no | 32941 | 15233 | 9345 |
| USA | 2023 | 45742 | 3510 | no | 224516 | 90680 | 56634 |
| USA | 2024 | 29283 | 162 | no | 336172 | 176531 | 122672 |

Investment values for the cited official reference series are *millions of US dollars*, covering **equity invested into privately held AI-related firms** from Crunchbase, not all national AI investment. The official 2024 patent values in these examples are marked incomplete. CSET patent families may be assigned by priority-filing country, which is not an ownership/nationality measure.

These are **not necessarily apples-to-apples series**. Numerical disagreement is a substantive provenance flag, **not proof** the supplied workbook is fabricated or incorrect. A different release, alternative source or transformations could explain it. **Do not replace the original inputs or quietly add any new observations.**

**Gate acceptance:** The workbook creator provides a verifiable precise CSET release/download URL and retrieval date, indicator codes, field filters, country mapping, year mapping, unit conversions, aggregation and rounding formulas, and source/completeness flags for **every AI input row**. An independent reproducibility script rebuilds the same dataset (or documents reconciled differences and obtains a methodological decision). World Bank API pulls for `TX.VAL.TECH.MF.ZS`, `NY.GDP.MKTP.KD.ZG`, and `SL.UEM.TOTL.ZS` also require release-date/value reconciliation without silently replacing the supplied professor dataset.

## Gate 2. Research question and construct validity: BLOCKED

The original supplied DOCX title calls the outcomes **employment and innovation**. The actual outcomes are **unemployment rate** and **high-technology exports as percentage of manufactured exports**. Neither is a direct observation of employment/jobs created or AI innovation. A legitimate, narrower title can explicitly name the observed outcomes, or the author/adviser must approve justified alternative measures. Do not relabel exports as an innovation count or unemployment as employment.

The original methodology narrative assumes that `ln(1+x)` predictors always permit elasticity interpretation, which is false for **level-outcome percentage** regressions: coefficients relate changes in log1p(x) to *percentage-point* changes in the outcome, not a fixed percent elasticity. Be precise near zero. Also, generic p-value cutoffs on Hansen/AR2 do not 'prove' instrument validity.

**Gate acceptance:** Hypotheses, measurable constructs, economic units, sign interpretation, formulae, sample definition, theory and limitations are mutually consistent and approved before final text.

## Gate 3. Prespecified target population and comparator: BLOCKED

The archived 2026-09-30 email asks to **examine feasibility of an Iran-similar country subset before estimation** and use 30 supplied countries if that cannot be justified. Iran is **not in the supplied panel**. Selecting an "Iran-like" subset post hoc based on desired coefficients is invalid.

**Gate acceptance:** Either select a peer subset using independently documented, pre-outcome, comparable Iran and country descriptors with explicit objective distance criteria (requires permission if additional comparison data are needed), or document why meaningful matching cannot be established from supplied inputs and retain all 30 countries as stated in the source request. No invented Iranian observations or hidden exclusions.

## Gate 4. Model/inference validity: INCOMPLETE

- With N=30 and T=9, system GMM is not automatically preferred or correctly identified. Time effects, persistence around unity, instrument relevance, common shocks and heterogeneity remain substantive risks.
- Source-moment rank is improved in round two but identification/exogeneity are not established by a non-rejected Hansen or Difference-in-Hansen statistic.
- Influence checks on removing CHN and USA showed coefficient sensitivity; one single AI-patent coefficient at p≈0.046 among many exploratory tests does not survive a credible multiplicity/robustness narrative.
- Complement with a theory-based, limited and prespecified alternative analysis, e.g. two-way FE with country-clustered uncertainty as transparent **associational** evidence, dynamic bias-corrected estimators when justified and implementable, and appropriately labelled static sensitivity. Be careful: T=9 makes Driscoll-Kraay and many large-T methods unreliable.
- If essential assumptions fail, present the project as a **descriptive, noncausal analysis**. Do not adjust instrument sets, countries or windows to obtain desirable p-values.

**Gate acceptance:** documented instrument relevance/exogeneity rationale, interpretable diagnostics, credible uncertainty and alternative-estimator consistency, with explicit absence of unsupported causal claims.

## Gate 5. Final reproducible deliverable and independent scientific review: PENDING

- One-command setup and execution from a clean checkout with a genuinely available Stata environment, including versioned `xtabond2`, deterministic inputs, output hash inventory and machine-checked tables against actual `.ster` and model logs.
- Independently review generated tables, manuscript, citations, theory, equations, Persian figures and precise language of hypotheses and conclusions.
- For Persian PDF/DOCX final deliverables, use Mikhak typography and visually review all pages before release.
- Merge or submit only if all blockers are resolved (or formally documented with scope reduced and approval for noncausal presentation).

## Immediate next action / division of work

**Assistant:** preserve source freeze; gather precise raw-data documentation and prepare a country/year/field/release/units reconciliation; audit WDI series; revise research questions and full report conditionally; then revisit estimation in a separate sensitivity branch only if supported.

**Dataset creator/user:** supply the original CSET extraction link, release/version, timestamp, raw tables and transformation code used to make the supplied Excel, OR state that no such provenance exists. The current source file and its dictionary are already available, so they do not need to be reuploaded. If provenance cannot be supplied, the scientific status must remain NO-GO for causal claims and any re-source/alternative design requires explicit approval.

**Next binary decision:** 
1. Provenance reconciled -> proceed to construct/identification and final independent review.
2. Provenance untraceable -> report data as unverified, stop claims and seek permission for an explicitly separate sourced-data research branch. Never silently substitute.
