"""Hard checks: no automatic causal approval from successful numerical fits."""
import csv, copy, json
from pathlib import Path
from validation.source_identification_gate import evaluate, MANIFEST, STATA
m=json.loads(MANIFEST.read_text(encoding="utf-8"))
with STATA.open(encoding="utf-8",newline="") as f:
    rows=list(csv.DictReader(f))
a=evaluate(m,rows)
assert a["current_causal_conclusion_approved"] is False
assert len(a["missing_source_fields"])==6
assert len(a["missing_identification_fields"])==6
assert a["difference_models_ar1_nonreject_at_5pct"]==4
assert a["investment_and_patent_coefficients_significant_at_5pct_by_abs_b_se"]==0
bad=copy.deepcopy(m)
bad["source_evidence"]["investment_metric_exact_match"]={"verified":True,"evidence_url":None}
try: evaluate(bad,rows)
except AssertionError: pass
else: raise AssertionError("Uncited source claim erroneously accepted")
try: evaluate(m,rows[:-1])
except AssertionError: pass
else: raise AssertionError("7-row incomplete Stata archive accepted")
print("PASS: source provenance and System GMM gate still blocked (real Stata 8 fits)")
