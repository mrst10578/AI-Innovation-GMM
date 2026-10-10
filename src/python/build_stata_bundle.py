"""Make verified portable ZIP with original Excel, dictionary, DTA, codes and research instructions."""
from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[2]
TARGET=ROOT/"dist/AI_Innovation_STATA_Ready.zip"
def sha(x):return hashlib.sha256(x).hexdigest()
def main():
    files=[]
    for folder in ("stata","src/python","src/r","src/gretl","validation","tests"):
        files += [p for p in (ROOT/folder).rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    files += [p for p in (ROOT/"data/raw").glob("*.xlsx")]
    files += [p for p in (ROOT/"data/processed").glob("*.dta")]
    files += [p for p in (ROOT/"sources").iterdir() if p.suffix in (".xlsx",".docx",".png")]
    files += [ROOT/s for s in ("MODEL_SPECIFICATION.md","DEFENSE_GUIDE_FA.md",
             "reports/RESEARCH_REPORT_FA.md","STATA_START_HERE_FA.md",
             "docs/PRE_STATA_FINAL_AUDIT_FA.md", "docs/AUDIT_REMEDIATION_STATUS_FA.md",
             "requirements-python.txt","config/project.json")]
    assert all(p.is_file() for p in files),[str(p) for p in files if not p.is_file()]
    assert (ROOT/"data/processed/stata_ready.dta") in files
    assert (ROOT/"data/raw/AI_Balanced_Panel (1).xlsx") in files
    unique=sorted(set(files),key=lambda p:p.as_posix())
    manifest={str(p.relative_to(ROOT)):{"sha256":sha(p.read_bytes()),"size":p.stat().st_size} for p in unique}
    TARGET.parent.mkdir(exist_ok=True,parents=True)
    with zipfile.ZipFile(TARGET,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for p in unique:z.write(p,arcname=str(p.relative_to(ROOT)))
        z.writestr("SOURCE_MANIFEST_SHA256.json",json.dumps(manifest,ensure_ascii=False,indent=2))
    with zipfile.ZipFile(TARGET) as z:
        assert z.testzip() is None
        for path,meta in manifest.items():
            assert sha(z.read(path))==meta["sha256"]
    print(json.dumps({"zip":str(TARGET),"bytes":TARGET.stat().st_size,
                      "files":len(manifest),"contains_Stata_output":False,
                      "contains_email_note":False,"contains_original_workbook":True,
                      "contains_real_audited_DTA":True}))
if __name__=="__main__":main()
