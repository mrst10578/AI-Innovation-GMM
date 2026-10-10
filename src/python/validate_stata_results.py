"""Post-run CSV quality check. It cannot certify causal validity."""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {(y, str(year), kind) for y in ('HighTech_Exports', 'Unemployment')
            for year in (2023, 2024) for kind in ('difference', 'system')}

def main(csv_path=None):
    p = Path(csv_path) if csv_path else ROOT / 'outputs/stata_model_summary.csv'
    if not p.is_file():
        print('ERROR: Stata CSV not present. Run licensed Stata first.', file=sys.stderr)
        return 2
    with p.open(encoding='utf-8-sig', newline='') as h:
        rows = list(csv.DictReader(h))
    seen = [(r['outcome'], r['period'], r['method']) for r in rows]
    duplicates = len(seen) != len(set(seen))
    missing = sorted(EXPECTED - set(seen))
    unknown = sorted(set(seen) - EXPECTED)
    failed = [r for r in rows if r.get('status') in {'SCRIPT_FAILED', 'EXECUTION_FAILED'}]
    flags = {':'.join((r['outcome'], r['period'], r['method'])):r.get('flags', '') for r in rows}
    coeff_absent = [r for r in rows if r.get('status') == 'REVIEW_REQUIRED'
                    and (r.get('invest_b', '').strip() in ('', '.', 'NA', 'NaN', 'nan')
                         or r.get('patent_b', '').strip() in ('', '.', 'NA', 'NaN', 'nan'))]
    out = {'rows':len(rows), 'model_script_or_estimation_failures':len(failed),
           'duplicates':duplicates, 'missing':missing, 'unexpected':unknown,
           'successful_model_coefficients_absent':len(coeff_absent),
           'diagnostic_flags':flags, 'causal_conclusion_approved':False,
           'state':'NEEDS_SCIENTIFIC_REVIEW'}
    dest = p.parent / 'stata_qc.json'
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False))
    return 0 if len(rows)==8 and not duplicates and not missing and not unknown and not failed and not coeff_absent else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else None))
