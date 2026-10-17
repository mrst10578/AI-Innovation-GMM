"""Create audited professor handoff zip (sans licensed Stata executable or font files)."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/"dist"
files=[
 "dist/AI_GMM_Professor_Review_FA.docx",
 "dist/AI_GMM_Professor_Review_FA.pdf",
 "data/raw/AI_Balanced_Panel (1).xlsx",
 "sources/AI_Balanced_Panel_Dictionary (1).xlsx",
 "sources/بررسی اثرات سرمایه گذاری و ثبت اختراعات هوش مصنوعی بر نرخ اشتغال و نوآوری با فناوری بالا (1).docx",
 "reports/PROFESSOR_PRE_ESTIMATION_20261017.csv",
 "reports/PROFESSOR_POST_ESTIMATION_20261017.csv",
 "reports/WDI_REFERENCE_RECONCILIATION_20261017.json",
 "reports/WDI_REFERENCE_ROW_COMPARISON_20261017.csv",
 "reports/STATA_REAL_gmm_diagnostics_20261017.csv",
 "reports/STATA_REAL_coefficients_20261017.csv",
 "reports/STATA_REAL_stress_v2_20261017.csv",
 "reports/STATA_REAL_followup_coefficients_20261017.csv",
 "reports/STATA_REAL_joint_hypotheses_20261017.csv",
 "reports/STATA_REAL_influence_CHN_USA_20261017.csv",
 "reports/STATA_REAL_alternative_associational_FE_20261017.csv",
 "reports/STATA_REAL_exploratory_fe_CD_20261017.csv",
 "reports/STATA_REAL_master_20261017.log",
 "reports/STATA_STRICT_master_20261017.log",
 "reports/STATA_STRICT_hightech_20261017.log",
 "reports/STATA_STRICT_unemployment_20261017.log",
 "reports/STATA_STRICT_TABLET_FINISH_20261017.log",
 "reports/STRICT_STATA_RERUN_RECEIPT_20261017.json",
 "reports/STATA_REAL_instrument_stress_v2_20261017.log",
 "reports/STATA_REAL_influence_CHN_USA_20261017.log",
 "reports/STATA_REAL_alternative_associational_FE_20261017.log",
 "reports/STATA_REAL_joint_hypotheses_20261017.log",
 "reports/STATA_EXTENDED_AUDIT_20261017_FA.md",
 "reports/CSET_REFERENCE_COMPARISON_20261017.json",
 "docs/PROFESSOR_RERUN_RUBRIC_AND_SOURCE_FREEZE_20261017.md",
 "docs/SCIENTIFIC_RELEASE_GATES_20261017.md",
 "docs/PROFESSOR_SUPPLIED_DATA_POLICY_FA.md",
 "docs/REFERENCE_MODEL_RATIONALE_FA.md",
 "docs/ADVERSARIAL_FINAL_REVIEW_FA_20261017.md",
 "docs/FINAL_HANDOFF_STATUS_FA.md",
 "stata/01_environment_and_data.do",
 "stata/02_pre_estimation.do",
 "stata/03_hightech_models.do",
 "stata/04_unemployment_models.do",
 "stata/05_post_estimation_and_export.do",
 "stata/06_export_real_coefficients.do",
 "stata/07_exploratory_pesaran_cd.do",
 "stata/08_instrument_stress.do",
 "stata/09_influence_china_usa.do",
 "stata/10_followup_coefficient_export.do",
 "stata/11_joint_ai_and_persistence.do",
 "stata/12_associational_fe.do",
 "stata/_run_one_model.do",
 "stata/RUN_ALL.do",
 "stata/TABLET_RUN.do",
 "config/project.json",
 "src/python/verify_wdi_reference.py",
 "src/python/verify_stata_strict_rerun.py",
]
READ_ME="""پوشه تحویل پژوهش | مخصوص بازبینی استاد

این مجموعه فقط از داده‌های ارائه‌شده توسط استاد، ارسال‌شده از طریق بهاره در ۳۰ سپتامبر ۲۰۲۶ استفاده می‌کند.
۱) AI_GMM_Professor_Review_FA.pdf / docx: متن پژوهش فارسی با فونت میخک.
۲) reports: خروجی‌های عددی و لاگ‌های واقعی Stata، بدون اعداد ساختگی.
۳) stata: do-fileهای بازتولید و تحلیل حساسیت.
۴) data/raw + sources: فایل‌های اصلی پژوهش، بدون تغییر.
۵) SHA256SUMS.txt: هش تمام فایل‌های بسته.

یادداشت علمی مهم: فایل‌های اولیه استاد عمداً دست‌کاری یا با انتشارهای دیگر CSET جایگزین نشده‌اند.
گزارش سیاست منبع استاد، معیار مشخصات مرجع و گزارش ممیزی علمی در پوشه docs قرار دارند.
گواهی اجرای سخت‌گیرانه جدید Stata و سه لاگ کامل تازه در پوشه reports قرار دارند.

تمام ۴۴ تخمین GMM و ۲۴ تخمین مقایسه‌ای Stata اجرا شده‌اند؛
این به معنی اثبات فروض علیت یا رفع تمام محدودیت‌های منبع داده نیست.
نتیجه‌گیری‌ها باید با برچسب تحلیل اکتشافی و ارتباط شرطی ارائه شوند.
سه متغیر منتسب به بانک جهانی در ۸۱۰ ردیف با API بررسی شدند: رشد اقتصادی و بیکاری ۲۷۰/۲۷۰، صادرات فناوری پیشرفته ۲۵۳/۲۷۰؛ علت ۱۷ اختلاف ثابت نشده است.
آرشیو .sterهای واقعی به دلیل قرار داشتن در حافظه تبلت، بخشی از این ZIP تولیدشده در GitHub نیست.
نسخه ZIP با فایل‌های .ster در تبلت با نام AI_STATA_REAL_OUTPUTS_20261017.zip باقی مانده است.
هیچ فایل فونتی داخل این بسته توزیع نشده است.
"""
def main():
    DIST.mkdir(exist_ok=True)
    missing=[f for f in files if not (ROOT/f).is_file()]
    if missing:raise FileNotFoundError("Missing required evidentiary inputs: "+str(missing))
    manifest=[]
    for file in files:
        b=(ROOT/file).read_bytes()
        manifest.append(f"{hashlib.sha256(b).hexdigest()}  {file}")
    payload="\n".join(manifest)+"\n"
    out=DIST/"AI_GMM_Professor_Handoff_20261017.zip"
    with ZipFile(out,"w",compression=ZIP_DEFLATED,compresslevel=9) as z:
        for file in files:
            z.write(ROOT/file,arcname=file)
        z.writestr("README_FA.txt",READ_ME.encode("utf-8"))
        z.writestr("SHA256SUMS.txt",payload.encode("utf-8"))
    with ZipFile(out) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(files)+2
    print("PROFESSOR_PACK_CREATED",out,"bytes",out.stat().st_size,
          "sha256",hashlib.sha256(out.read_bytes()).hexdigest(),
          "total_members",len(files)+2)
if __name__=="__main__":main()
