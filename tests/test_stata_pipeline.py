"""Synthetic CI assertions, never actual econometric observations."""
from pathlib import Path
import tempfile, csv, json
from src.python.validate_stata_results import EXPECTED, main

def fake_rows():
    return [{'outcome':y,'period':period,'method':method,'status':'REVIEW_REQUIRED',
             'flags':'SOURCE_UNVERIFIED;NO_DIFFERENCE_HANSEN','invest_b':'0.1','patent_b':'0.2'}
            for y, period, method in sorted(EXPECTED)]

def run_case(rows):
    with tempfile.TemporaryDirectory() as td:
        file = Path(td)/'stata_model_summary.csv'
        with file.open('w',newline='',encoding='utf-8') as f:
            out=csv.DictWriter(f,fieldnames=['outcome','period','method','status','flags','invest_b','patent_b'])
            out.writeheader();out.writerows(rows)
        result=main(str(file))
        check=json.loads((Path(td)/'stata_qc.json').read_text())
        assert check['causal_conclusion_approved'] is False
        return result,check

def test_stata_result_audit_protects_against_fake_success():
    rows=fake_rows()
    assert run_case(rows)[0] == 0
    assert run_case(rows[:-1])[0] == 1
    assert run_case(rows+[rows[0]])[0] == 1
    rows[0]['status']='EXECUTION_FAILED'
    assert run_case(rows)[0] == 1
    rows=fake_rows(); rows[0]['invest_b']=''
    assert run_case(rows)[0] == 1

if __name__=='__main__':
    test_stata_result_audit_protects_against_fake_success()
    print('PASS: 5 synthetic Stata output validation cases (NOT Stata execution)')
