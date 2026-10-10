"""Regression test: CSV truncation and field shift must fail in CI.
Tests use intentionally corrupted COPIES; authentic stored file is not changed.
"""
import csv
import tempfile
from pathlib import Path
from validation.audit_real_stata import SOURCE,load_verified_rows
def run():
    correct=load_verified_rows()
    assert len(correct)==8
    assert len(correct[3])==22
    header=None
    with SOURCE.open(encoding="utf-8",newline="") as fh:
        dat=list(csv.reader(fh))
    header=dat[0]
    assert len(header)==22
    # 2023 System export must have all 22 values, including patent_b=-0.12627859
    assert len(dat[4])==22
    assert dat[4][18]=="-.12627859"
    assert dat[4][19]==".19012202"
    assert dat[4][20]==".2001714"
    assert dat[4][21]==".13848077"
    with tempfile.TemporaryDirectory() as d:
        tmp=Path(d)/"mutated.csv"
        for case in ("missing_column","patent_shift","invalid_gdp_se"):
            rows=[r.copy() for r in dat]
            if case=="missing_column": rows[4].pop(18)
            elif case=="patent_shift": rows[4][18]=".19012202"
            elif case=="invalid_gdp_se": rows[4][21]=""
            with tmp.open("w",newline="",encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            try: load_verified_rows(tmp)
            except AssertionError: print("MUTATION_REJECTED",case)
            else: raise AssertionError("Corrupt archive was silently accepted: "+case)
    print("VERIFIED_ORIGINAL_REAL_STATA_ARCHIVE_ALL_8_ROWS_22_FIELDS")
if __name__=="__main__":
    run()
