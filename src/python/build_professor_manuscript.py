"""Build professor-review Persian DOCX/PDF directly from logged authentic Stata outputs.

This does not certify causal validity, change inputs or replace data.
Requires python-docx, LibreOffice and locally installed Mikhak font files.
No fonts are ever included in deliverables.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
REP = ROOT / "reports"
DIST = ROOT / "dist"
BLUE = RGBColor(25, 49, 79)
TEAL = RGBColor(0, 110, 120)
GREY = RGBColor(78, 86, 97)
FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

def fnum(v, digits=3):
    if v is None or str(v).strip() in ("", ".", "nan"):
        return "گزارش‌نشده"
    try:
        f = float(v)
        if abs(f) < 0.0005 and f != 0:
            return "کمتر از ۰٫۰۰۱"
        return f"{f:.{digits}f}".translate(FA).replace(".", "٫").replace("-", "−")
    except (ValueError, TypeError):
        return str(v).translate(FA)

def num(v):
    return str(v).translate(FA)

def pnum(v):
    if v is None or str(v).strip() in ("", "."):
        return "ناموجود"
    try:
        value=float(v)
        return "کمتر از ۰٫۰۰۱" if value < 0.001 else fnum(value,3)
    except (TypeError,ValueError):
        return "ناموجود"

def csv_rows(filename):
    with (REP / filename).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def verify():
    names = {
        "PROFESSOR_PRE_ESTIMATION_20261017.csv": 5,
        "PROFESSOR_POST_ESTIMATION_20261017.csv": 16,
        "STATA_REAL_alternative_associational_FE_20261017.csv": 24,
        "STATA_REAL_followup_coefficients_20261017.csv": 112,
        "STATA_REAL_joint_hypotheses_20261017.csv": 16,
        "STATA_REAL_gmm_diagnostics_20261017.csv": 16,
    }
    for name, n in names.items():
        rows = csv_rows(name)
        if len(rows) != n:
            raise RuntimeError(f"Input evidence row count invalid: {name}: {len(rows)} instead of {n}")
    data = ROOT / "data/raw/AI_Balanced_Panel (1).xlsx"
    original_sha = "4f9bf76658d1f495d3eb3e39b226bb5ba6ac39446b35e41bfce4a2aab65d0434"
    if hashlib.sha256(data.read_bytes()).hexdigest() != original_sha:
        raise RuntimeError("Original 30-country Excel hash differs. Do not publish.")
    strict=json.loads((REP/"STRICT_STATA_RERUN_RECEIPT_20261017.json").read_text(encoding="utf-8"))
    if strict["status"]!="STRICT_STATA_BASELINE_RERUN_VERIFIED" or strict["baseline_gmm_estimates"]!=16 or strict["exit_code"]!=0:
        raise RuntimeError("Strict real Stata rerun has not passed independent verification")
    l = (REP / "STATA_REAL_alternative_associational_FE_20261017.log").read_text()
    if "ALTERNATIVE_SUCCESS_COUNT=24" not in l or "ALTERNATIVE_FAILURE_COUNT=0" not in l:
        raise RuntimeError("New FE log does not attest to 24 successful fits")

def rtl_paragraph(p):
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    ppr = p._p.get_or_add_pPr()
    bidi = ppr.find(qn("w:bidi"))
    if bidi is None:
        bidi = OxmlElement("w:bidi"); ppr.append(bidi)
    bidi.set(qn("w:val"), "1")
    return p

def set_font(run, name="Mikhak", size=10, bold=None, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    if bold is not None: run.bold = bold
    if color: run.font.color.rgb = color
    rpr = run._r.get_or_add_rPr()
    rfonts = rpr.rFonts
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.insert(0, rfonts)
    for x in ("ascii","hAnsi","eastAsia","cs"):
        rfonts.set(qn("w:"+x), name)
    return run

def add_p(doc, txt="", *, style=None, color=None, bold=False, size=10, after=4, keep_next=False):
    p=doc.add_paragraph(style=style)
    rtl_paragraph(p)
    p.paragraph_format.space_after=Pt(after)
    p.paragraph_format.line_spacing=1.17
    if keep_next: p.paragraph_format.keep_with_next = True
    set_font(p.add_run(txt), name="Mikhak SemiBold" if size==13 else "Mikhak", size=size, color=color, bold=bold)
    return p

def heading(doc, title, level=1):
    p=doc.add_paragraph()
    rtl_paragraph(p)
    p.paragraph_format.space_before=Pt(12 if level==1 else 8)
    p.paragraph_format.space_after=Pt(6)
    p.paragraph_format.keep_with_next=True
    set_font(p.add_run(title), name="Mikhak", size=14 if level==1 else 11, bold=True if level==1 else False, color=BLUE if level==1 else TEAL)
    return p

def bullet(doc, s):
    return add_p(doc, "•  "+s, size=9.7, after=4)

def shade(cell, fill="18314F"):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)

def tab(doc, headers, rows, widths=None, font_size=8):
    t=doc.add_table(rows=1, cols=len(headers))
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.style="Table Grid"
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i]
        c.text=""
        shade(c)
        p=rtl_paragraph(c.paragraphs[0])
        set_font(p.add_run(str(h)),name="Mikhak Medium",size=font_size,bold=False,color=RGBColor(255,255,255))
        c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    for j, values in enumerate(rows):
        cells=t.add_row().cells
        for i,v in enumerate(values):
            c=cells[i];c.text=""
            if j%2:shade(c,"F0F5F7")
            p=rtl_paragraph(c.paragraphs[0])
            p.paragraph_format.space_after=Pt(1)
            p.paragraph_format.space_before=Pt(1)
            set_font(p.add_run(str(v)),name="Mikhak Medium",size=font_size)
            c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    doc.add_paragraph()
    return t

def page_field(section):
    footer=section.footer
    p=footer.paragraphs[0]
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run("پژوهش سرمایه‌گذاری و پتنت هوش مصنوعی | نسخه بازبینی استاد | صفحه "),size=8,color=GREY)
    fld=OxmlElement("w:fldSimple");fld.set(qn("w:instr"),"PAGE");p._p.append(fld)

def create_docx():
    verify()
    DIST.mkdir(exist_ok=True)
    doc=Document()
    sec=doc.sections[0]
    sec.page_width=Cm(21)
    sec.page_height=Cm(29.7)
    sec.top_margin=Cm(1.8)
    sec.bottom_margin=Cm(1.7)
    sec.left_margin=Cm(2)
    sec.right_margin=Cm(2)
    page_field(sec)
    style=doc.styles["Normal"]
    style.font.name="Mikhak";style.font.size=Pt(10)
    style.paragraph_format.space_after=Pt(5)
    # Set the named Mikhak typeface even for complex-script Persian text.
    st_rpr=style.element.get_or_add_rPr()
    rfonts=st_rpr.rFonts
    if rfonts is None:
        rfonts=OxmlElement("w:rFonts");st_rpr.insert(0,rfonts)
    for a in ("ascii","hAnsi","eastAsia","cs"):rfonts.set(qn("w:"+a),"Mikhak")
    add_p(doc,"گزارش پژوهشی | نسخه قابل بازبینی استاد",size=10,bold=True,color=TEAL,after=18)
    add_p(doc,"رابطه سرمایه‌گذاری و ثبت اختراعات هوش مصنوعی با سهم صادرات فناوری پیشرفته و نرخ بیکاری",size=19,bold=True,color=BLUE,after=10)
    add_p(doc,"تحلیل داده‌های تابلویی ۳۰ کشور، ۲۰۱۶ تا ۲۰۲۴",size=13,bold=False,color=TEAL,after=10)
    add_p(doc,"داده: فایل اصلی ارسال‌شده در ایمیل ۳۰ سپتامبر ۲۰۲۶ | نرم‌افزار: Stata/MP 17 و xtabond2",size=9,color=GREY,after=12)
    add_p(doc,"وضعیت علمی: تخمین‌ها و آزمون‌ها اجرا شده‌اند؛ شناسایی علّی و اصالت کامل زنجیره منبع AI هنوز تأیید نشده است. این سند برای بررسی استاد تهیه شده، نه ادعای اثبات رابطه علّی.",size=10,bold=True,color=BLUE,after=18)
    heading(doc,"چکیده")
    add_p(doc,"هدف پژوهش، بررسی ارتباط سرمایه‌گذاری و درخواست‌های ثبت اختراع هوش مصنوعی با دو پیامد قابل‌اندازه‌گیری شامل سهم صادرات با فناوری پیشرفته از صادرات صنعتی و نرخ بیکاری است. داده‌های ۳۰ کشور طی سال‌های ۲۰۱۶ تا ۲۰۲۴ در یک پنل متوازن با ۲۷۰ مشاهده بررسی شدند. مشخصات پویای GMM تفاضلی و سیستمی در کنار تخمین‌های اثرات ثابت کشور و سال، با خطاهای استاندارد خوشه‌ای، آزمون‌های ریشه واحد و تحلیل حساسیت به حذف ۲۰۲۴ و کشورهای چین و آمریکا اجرا شدند. در مشخصات گسترش‌یافته، نقص درجه آزادی آزمون‌های ابزاری و هشدار عددی برخی مشخصات اولیه بهبود یافت؛ بااین‌حال نتیجه آزمون‌های مشترک AI معناداری قاطع نشان نداد و پایداری ضرایب به مشخصات حساس ماند. این شواهد صرفاً برای بیان ارتباطات شرطی اکتشافی قابل استفاده‌اند، نه استنتاج علّی.")
    add_p(doc,"واژگان کلیدی: هوش مصنوعی؛ اختراعات؛ سرمایه‌گذاری؛ صادرات فناوری پیشرفته؛ بیکاری؛ System GMM؛ پنل کوتاه",size=9,color=GREY,after=14)
    heading(doc,"۱. مسئله و دامنه استنباط")
    add_p(doc,"موضوع فایل اولیه «اشتغال و نوآوری» است، اما داده‌های قابل دسترس، مستقیماً نرخ بیکاری و سهم صادرات فناوری پیشرفته را اندازه می‌گیرند؛ بنابراین عنوان و فرضیه‌ها در این گزارش به شاخص‌های مشاهده‌شده محدود شده‌اند. افزایش نرخ بیکاری معادل کاهش عدد اشتغال و افزایش سهم صادرات فناوری پیشرفته معادل افزایش تعداد اختراعات نیست.")
    add_p(doc,"فرضیه اول: ضرایب شرطی لگاریتم سرمایه‌گذاری و پتنت AI در معادله سهم صادرات فناوری پیشرفته با صفر تفاوت دارند. فرضیه دوم: همین ضرایب در معادله نرخ بیکاری با صفر تفاوت دارند. فرضیه مشترک در هر معادله نیز برابر صفر بودن هم‌زمان دو ضریب AI است.")
    add_p(doc,"کنترل بازتولید: اجرای مستقل و سخت‌گیرانه Stata/MP 17 پس از اصلاح اسکریپت‌ها دوباره انجام شد؛ ۱۶ مدل اصلی از ۱۶ مدل، هر ۱۰ آزمون IPS/Fisher پیش از تخمین و ۱۶ فایل واقعی .ster تأیید شدند. رسید محاسبات و سه لاگ جدید در پیوست نتایج است.",size=9,color=TEAL)
    heading(doc,"۲. منشأ، نمونه و متغیرها")
    add_p(doc,"داده‌های این نسخه طبق تأیید صاحب پروژه توسط استاد ارائه و از طریق بهاره در سه پیوست ایمیل ۳۰ سپتامبر ۲۰۲۶ شامل فایل Excel پنل، فرهنگ داده و متن روش تحقیق ارسال شده‌اند. فایل اصلی ۱۹٬۹۰۱ بایت، بدون تغییر و با هش ثبت‌شده در پیوست بازتولید حفظ شده است. ۳۰ کشور و ۹ سال به‌صورت متوازن حضور دارند و داده گمشده و ردیف تکراری کشور–سال مشاهده نشد.")
    tab(doc,["متغیر","تعریف عملیاتی و واحد","نقش"],[
        ["HighTech_Exports","درصد صادرات محصولات فناوری‌بالا از صادرات صنعتی (بانک جهانی: TX.VAL.TECH.MF.ZS)","پیامد اول"],
        ["Unemployment","نرخ بیکاری، درصد نیروی کار (SL.UEM.TOTL.ZS)","پیامد دوم"],
        ["AI_Investment","ارزش اسمی سرمایه‌گذاری AI در فایل استاد؛ واحد/سری بالادستی مشخص نشده","توضیحی اصلی"],
        ["AI_Patents","تعداد درخواست‌های ثبت اختراع مرتبط با AI","توضیحی اصلی"],
        ["GDP_Growth","نرخ رشد حقیقی GDP، درصد سالانه (NY.GDP.MKTP.KD.ZG)","کنترل"],
        ["ISO3 / Year","شناسه کشور / سال ۲۰۱۶–۲۰۲۴","شاخص پنل"]
    ],font_size=8)
    add_p(doc,"ایران در پنل وجود ندارد. به دلیل نبود مجموعه شاخص‌های مستقل و قابل دفاع برای سنجش شباهت به ایران، زیرگروه «کشورهای مشابه ایران» از داده موجود قابل تشکیل نیست؛ مطابق دستور مکمل ایمیل، کل ۳۰ کشور حفظ شده‌اند. این تصمیم باید در متن ارسالی به استاد درج شود.")
    heading(doc,"۲-الف. ممیزی مستقل شاخص‌های بانک جهانی",level=2)
    add_p(doc,"برای اطمینان از صحت سه شاخص منتسب به بانک جهانی، هر ۲۷۰ مشاهده کشور–سال با داده رسمی API بانک جهانی (نسخه دارای تاریخ به‌روزرسانی ۸ اکتبر ۲۰۲۶) به‌صورت فقط‌خواندنی تطبیق داده شد. معیار تطابق اختلاف مطلق کمتر یا مساوی ۰٫۰۰۱ بود.")
    tab(doc,["متغیر در پنل","تطابق با API","اختلاف‌ها","کد شاخص رسمی"],[
        ["رشد واقعی GDP","۲۷۰ از ۲۷۰","۰","NY.GDP.MKTP.KD.ZG"],
        ["نرخ بیکاری","۲۷۰ از ۲۷۰","۰","SL.UEM.TOTL.ZS"],
        ["سهم صادرات فناوری پیشرفته","۲۵۳ از ۲۷۰","۱۷","TX.VAL.TECH.MF.ZS"]
    ],font_size=8.3)
    add_p(doc,"بزرگ‌ترین اختلاف مربوط به فرانسه در ۲۰۲۰ است: مقدار پنل ۲۱٫۱۹۲ و مقدار نسخه فعلی بانک جهانی ۲۲٫۵۴۰، اختلاف ۱٫۳۴۸ واحد درصدی. تاریخ به‌روزرسانی مرجع پس از ارسال ایمیل بهاره است؛ بنابراین بازنگری داده‌ها یک توضیح ممکن است، نه نتیجه اثبات‌شده. همه اختلاف‌ها و ۸۱۰ مقایسه تک‌ردیفی در پیوست WDI ثبت شدند. هیچ سطر یا عددی در فایل مبنای تخمین جایگزین نشده است.")
    
    heading(doc,"۳. معادلات و راهبرد تخمین")
    add_p(doc,"برای هر یک از دو پیامد Y، مشخصه پویا به صورت زیر است:")
    add_p(doc,"Y(i,t) = αY(i,t−1) + β۱ ln(1+Investment(i,t)) + β۲ ln(1+Patents(i,t)) + γ GDP_Growth(i,t) + μ(i) + τ(t) + ε(i,t)",size=9.5,bold=True)
    add_p(doc,"مقادیر صفر سرمایه‌گذاری با تبدیل ln(1+x) حفظ شده‌اند. چون پیامدها در واحد درصد و متغیرهای اصلی در لگاریتم (۱+مقدار) هستند، ضرایب AI تغییرات برحسب «واحد درصدی پیامد» در پاسخ به تغییر لگاریتم متغیر را نشان می‌دهند و نباید بی‌قیدوشرط به‌عنوان کشش درصدی تفسیر شوند.")
    add_p(doc,"مدل GMM سیستمی و تفاضلی با xtabond2، ابزارهای فروکاسته‌شده collapse، خطاهای robust، اثرات سال و پنجره‌های محدود وقفه برآورد شده است. در دور اصلاحی، رشد اقتصادی در یک گروه از مشخصات با وقفه‌های ۲ تا ۳ درون‌زا در نظر گرفته شد. انتخاب یک نسخه براساس معنی‌داری ضرایب مجاز نیست. فروض لحظه‌ای در معادله تفاضلی مستلزم نبود همبستگی ابزارهای گذشته با شوک فعلی‌اند؛ System GMM علاوه‌برآن محدودیت‌های مربوط به ابزارهای معادله سطح می‌خواهد. اعتبار اقتصادی این فروض صرفاً از آزمون Hansen نتیجه نمی‌شود.")
    heading(doc,"۴. آزمون‌های پیش از تخمین")
    pre=csv_rows("PROFESSOR_PRE_ESTIMATION_20261017.csv")
    tab(doc,["متغیر","IPS p","Fisher p","توضیح"],[
        [v["variable"],pnum(v["IPS_p"]),pnum(v["Fisher_ADF_P_p"]),
         "شواهد مانایی" if float(v["IPS_p"])<.05 and float(v["Fisher_ADF_P_p"])<.05 else
         "ناسازگاری دو آزمون" if (float(v["IPS_p"])<.05)!=(float(v["Fisher_ADF_P_p"])<.05) else "عدم رد ریشه واحد"]
        for v in pre],font_size=8.5)
    add_p(doc,"فرض صفر IPS و Fisher وجود ریشه واحد در همه مقاطع است. T=۹ و احتمال وابستگی مقطعی، توان و اندازه آزمون را محدود می‌کند. عدم رد ریشه واحد، تأیید قطعی نامانایی نیست. آزمون همبستگی pairwise و VIF نیز اجرا شد؛ میانگین VIF در رگرسیون‌های کمکی ۲٫۰۴ گزارش شده است. VIF تجمیعی معیار کامل هم‌خطی «درون‌کشوری» نیست.")
    heading(doc,"۴-الف. تعیین مشخصه مرجع برای تفسیر",level=2)
    add_p(doc,"در گزارش دو معادله، مشخصات S23_E تا سال ۲۰۲۴ تنها به‌عنوان مرجع شفاف مقایسه معرفی می‌شوند: کل نمونه استاد حفظ شده، GDP Growth درون‌زا ابزارگذاری شده، پنجره وقفه محدود و ابزارها فروکاسته شده‌اند. مشخصه مرجع پس از مشاهده شبکه نتایج برای ساده‌سازی ارائه انتخاب شده، نه به‌عنوان مدل پیش‌ثبت‌شده از ابتدای تحقیق یا تنها مدل صحیح؛ همه مدل‌های جایگزین و نتیجه‌های نامطلوب نیز گزارش می‌شوند.")
    heading(doc,"۵. گزارش تشخیصی GMM مطابق درخواست استاد")
    add_p(doc,"جدول زیر چهار نمونه از هشت مشخصه سیستمی اصلاح‌شده را نشان می‌دهد. جزئیات همه ۱۶ مشخصه در فایل CSV پیوست وجود دارد. کدهای S23_E به ابزارگذاری رشد اقتصادی به عنوان متغیر درون‌زا و وقفه گسترده اشاره می‌کنند.")
    diag={r["model"]:r for r in csv_rows("PROFESSOR_POST_ESTIMATION_20261017.csv")}
    keys=["hi_2024_S23_E","hi_2023_S23_E","un_2024_S23_E","un_2023_S23_E"]
    tab(doc,["مدل","ابزار/کشور","AR(1) p","AR(2) p","Hansen p","Diff-Hansen p"],[
        [k.replace("_"," "),f'{num(diag[k]["instrument_count"])}/{num(diag[k]["groups"])}',
         pnum(diag[k]["AR1_p"]),pnum(diag[k]["AR2_p"]),pnum(diag[k]["Hansen_robust_p"]),
         pnum(diag[k]["level_instrument_diff_Hansen_p"])] for k in keys],font_size=8.2)
    add_p(doc,"در مجموع ۱۶ مشخصه دور دوم، تعداد ابزارها در همه موارد از ۳۰ کشور کمتر بود؛ هر ۱۶ آزمون AR(2) مقدار احتمال بالاتر از ۰٫۰۵ داشتند؛ تنها ۷ مورد از ۱۶ آزمون AR(1) در سطح ۵٪ معنادار بود؛ در ۱۴ مورد p آزمون Hansen بین ۰٫۰۵ و ۰٫۹۵ قرار داشت. برای هشت مدل سیستمی، آزمون حذف ابزارهای معادله سطوح ۳ یا ۴ درجه آزادی داشت. به‌هیچ‌وجه نمی‌توان از «عدم رد Hansen» نتیجه گرفت ابزارها قطعاً برون‌زا هستند.")
    add_p(doc,"در مشخصات اولیه و آزمون‌های حذف چین/آمریکا هشدار تکین‌بودن ماتریس گشتاورها وجود داشت. در ۱۶ مدل اصلاحی این هشدار مشاهده نشد؛ این بهبود عددی است، نه اثبات شناسایی.")
    heading(doc,"۶. ضرایب منتخب GMM: مدل‌های سیستمی دومرحله‌ای با GDP درون‌زا")
    coeff=csv_rows("STATA_REAL_followup_coefficients_20261017.csv")
    cindex={(r["model"],r["term"]):r for r in coeff}
    data=[]
    for k in keys:
        m="stress_"+k
        lagterm="L.HighTech_Exports" if k.startswith("hi") else "L.Unemployment"
        ai=cindex[(m,"ln_ai_investment")]
        patent=cindex[(m,"ln_ai_patents")]
        ar=cindex[(m,lagterm)]
        data.append([k.replace("_"," "),fnum(ar["estimate"]),
          fnum(ai["estimate"])+" (SE "+fnum(ai["se"])+"؛ p "+pnum(ai["p_value"])+")",
          fnum(patent["estimate"])+" (SE "+fnum(patent["se"])+"؛ p "+pnum(patent["p_value"])+")"])
    tab(doc,["مدل","ضریب وقفه","β سرمایه AI (SE؛ p)","β پتنت AI (SE؛ p)"],data,font_size=7.7)
    add_p(doc,"در این چهار مشخصه ازپیش‌تعیین‌شده، ضرایب سرمایه‌گذاری و پتنت در سطح ۵٪ به‌طور منفرد معنادار نیستند. ضریب وقفه در برخی نمونه‌ها نزدیک یا بالاتر از یک است. این نتیجه نه اثبات «نبود اثر AI» است و نه مجوز گزارش اثر علّی.")
    heading(doc,"۷. برآورد جایگزین: اثرات ثابت دوطرفه با خوشه‌بندی کشوری")
    fe=csv_rows("STATA_REAL_alternative_associational_FE_20261017.csv")
    lookup={r["model"]:r for r in fe}
    fe_rows=[]
    for outcome,prefix in [("سهم صادرات فناوری","hi"),("نرخ بیکاری","un")]:
        for end in (2024,2023):
            x=lookup[f"{prefix}_{end}_NONE_staticFE"]
            fe_rows.append([outcome,num(end),fnum(x["lninv_b"])+" ("+pnum(x["lninv_p"])+")",
                             fnum(x["lnpat_b"])+" ("+pnum(x["lnpat_p"])+")",
                             fnum(x["r2"])])
    tab(doc,["پیامد","تا سال","β سرمایه AI (p)","β پتنت AI (p)","R² درون"],fe_rows,font_size=8.2)
    add_p(doc,"این مدل‌ها با اثر ثابت کشور و سال و خطای استاندارد خوشه‌ای در کشور اجرا شدند. اثرات ثابت ایستا برای تفسیر ارتباط شرطی مناسب‌تر از ادعای علّیت هستند، ولی تورش ناشی از درون‌زایی متغیرهای اصلی و خطاهای اندازه‌گیری را حذف نمی‌کنند. نسخه‌های دارای وقفه پاسخ با FE و OLS نیز به عنوان مقایسه محاسبه شدند؛ FE پویا به دلیل T کوتاه دارای تورش Nickell و OLS پویا دارای مشکل درون‌زایی است.")
    heading(doc,"۸. آزمون استحکام نسبت به نمونه و کشورها")
    add_p(doc,"در آزمایش‌های ازپیش‌ثبت‌شده، نمونه تا ۲۰۲۳ (حذف سال ۲۰۲۴) و نمونه‌های حذف چین، حذف آمریکا و حذف هر دو کشور با همان ورودی اولیه آزموده شد. ۱۲ بازبرآورد GMM مربوط به حذف کشورها و ۱۶ مدل اثر ثابت ایستا نیز موجودند. برای نمونه، ضریب پتنت در معادله بیکاری مدل FE با همه کشورها، در نمونه تا ۲۰۲۴ مقدار احتمال ۰٫۰۵۷ داشت؛ در نمونه تا ۲۰۲۳ برابر ۰٫۰۲۷ شد. تغییر نتیجه با افق زمانی، علامت هشدار است و نباید از میان آن‌ها صرفاً نتیجه معنادار انتخاب شود.")
    add_p(doc,"در سال ۲۰۲۴، چین حدود ۹۲٫۰۷٪ درخواست‌های پتنت AI و آمریکا حدود ۷۱٫۵۲٪ ارزش اسمی سرمایه‌گذاری AI ثبت‌شده نمونه را به خود اختصاص داده‌اند. این ارقام از جمع خود داده‌های بهاره محاسبه شده‌اند. چنین تمرکزی، حساسیت به کشورهای بزرگ و کیفیت تعریف شاخص‌ها را مهم می‌کند.")
    heading(doc,"۹. آزمون فرضیه‌های مشترک و نتیجه‌گیری")
    wald=csv_rows("STATA_REAL_joint_hypotheses_20261017.csv")
    assert len(wald)==16
    both=sum(float(r["joint_ai_p"])<.05 for r in wald)
    lag=sum(float(r["persistence_equal1_p"])<.05 for r in wald)
    add_p(doc,f"در ۱۶ تخمین دور دوم، فرض صفر مشترک برابری هر دو ضریب AI با صفر در سطح ۵٪ در {num(both)} مدل رد شد. فرض صفر برابر یک بودن ضریب وقفه نیز در {num(lag)} مدل رد شد. با توجه به اندازه کوچک پنل و توان محدود آزمون‌ها، عدم رد هیچ‌یک از این فرض‌ها اثبات درست‌بودن آن‌ها نیست.")
    add_p(doc,"نتیجه کلی: با نمونه و روش‌های فعلی، شواهد کافی و پایدار برای ادعای یک اثر علّی و معنادار سرمایه‌گذاری و پتنت AI بر دو پیامد در همه مشخصات به دست نیامده است. نتیجه‌ای که با اطمینان بیشتری می‌توان عرضه کرد، محدودبودن قدرت شناسایی مدل‌ها و حساسیت یافته‌ها به مشخصات و نمونه است.")
    heading(doc,"۱۰. محدودیت‌ها و ملاحظات اجباری پیش از تأیید استاد")
    for item in [
        "منبع سطح‌بالای فرهنگ داده‌ها CSET و بانک جهانی ذکر شده، اما شناسه نسخه، تاریخ استخراج و فرمول تجمیع دقیق AI در فایل‌های اولیه مشخص نیست؛ اختلاف با نسخه رسمی دیگر CSET اثبات خطا نیست، ولی منشأ قابل بازتولید را هنوز کامل نمی‌کند.",
        "سهم صادرات فناوری پیشرفته، شاخص جانشینِ رقابت‌پذیری و نه اندازه‌گیری مستقیم «نوآوری» است؛ نرخ بیکاری نیز مستقیماً نرخ اشتغال را اندازه نمی‌گیرد.",
        "پنل فقط ۳۰ کشور و حداکثر ۹ سال دارد و ایران در آن وجود ندارد؛ زیرگروه کشورهایی مشابه ایران با همین ورودی قابل‌دفاع نیست.",
        "فرض‌های شناسایی System GMM و تناسب ابزارهای وقفه با شوک‌های مشترک نیازمند توجیه نظری مستقل هستند؛ عبور از آزمون‌های متداول معادل اثبات آن‌ها نیست.",
        "سال ۲۰۲۴ برای پتنت‌ها ممکن است مشمول تأخیر گزارش باشد؛ از داده خام امکان اثبات علت نوسانات وجود ندارد.",
        "رد نسخه قدیمی توسط استاد دلیل دقیق و مکتوب ندارد؛ نباید ادعا کرد صرف اجرای آزمون‌های این نسخه همه اعتراض‌های احتمالی را رفع کرده است."
    ]: bullet(doc,item)
    heading(doc,"پیوست الف. جدول کامل ۱۶ مشخصه اصلاحی GMM")
    add_p(doc,"همه اعداد جدول‌های زیر از خروجی واقعی xtabond2 استخراج شده‌اند. نماد «—» به معنای آزمون مربوط‌نبودن به مشخصه تفاضلی است؛ ناموجودبودن آزمون نباید با صفر جایگزین شود.")
    for pname,pref in [("صادرات فناوری پیشرفته","hi_"),("نرخ بیکاری","un_")]:
        subset=[r for r in csv_rows("PROFESSOR_POST_ESTIMATION_20261017.csv") if r["model"].startswith(pref)]
        tab(doc,["شناسه مدل","مشاهده","ابزار","AR(1) p","AR(2) p","Sargan p","Hansen p"],[
            [r["model"].replace("hi_","").replace("un_","").replace("_"," "),
             num(240 if r["sample_end"]=="2024" and r["GMM_type"]=="system" else
                 210 if (r["sample_end"]=="2024" and r["GMM_type"]=="difference") or
                         (r["sample_end"]=="2023" and r["GMM_type"]=="system") else 180),
             num(r["instrument_count"]), pnum(r["AR1_p"]),pnum(r["AR2_p"]),
             pnum(r["Sargan_nonrobust_p"]),pnum(r["Hansen_robust_p"])] for r in subset],font_size=7.5)
        tab(doc,["مدل","درجه آزادی حذف ابزار سطح","Difference-in-Hansen p","آزمون مشترک AI p"],[
            [r["model"].replace("hi_","").replace("un_","").replace("_"," "),
             num(r["level_exclusion_hansen_df"]) if r["level_exclusion_hansen_df"] else "نامربوط",
             pnum(r["level_instrument_diff_Hansen_p"]) if r["level_instrument_diff_Hansen_p"] else "نامربوط",
             pnum(r["joint_AI_Wald_p"])] for r in subset],font_size=8)
        add_p(doc,"پنل "+pname+"؛ شناسه‌های D و S به‌ترتیب تفاضلی و سیستمی‌اند؛ X برون‌زایی موقت GDP و E ابزارگذاری GDP با وقفه را نشان می‌دهد.",size=8.6,color=GREY)
    add_p(doc,"در این جدول هر «p بزرگ» صرفاً نشان‌دهنده عدم رد فرض صفر آزمون متناظر است؛ AR(2)، Hansen و Difference-in-Hansen به تنهایی شناسایی علّی را تأیید نمی‌کنند.")
    heading(doc,"پیوست ب. حساسیت مدل اثرات ثابت به حذف کشور و سال")
    for pname,prefix in [("صادرات فناوری پیشرفته","hi"),("نرخ بیکاری","un")]:
        records=[r for r in fe if r["family"]=="static_twFE" and r["model"].startswith(prefix+"_")]
        tab(doc,["تا سال","حذف کشور","گروه‌ها","β سرمایه AI (p)","β پتنت AI (p)"],[
            [num(r["cutoff"]),{"NONE":"هیچ","CHN":"چین","USA":"آمریکا","BOTH":"هر دو"}[r["exclusion"]],
             num(r["Ng"]),fnum(r["lninv_b"])+" ("+pnum(r["lninv_p"])+")",
             fnum(r["lnpat_b"])+" ("+pnum(r["lnpat_p"])+")"] for r in records],font_size=8)
        add_p(doc,"پیامد "+pname+"؛ اثرات ثابت کشور و سال و خطاهای خوشه‌ای به تفکیک کشور؛ تحلیل اکتشافی، نه علّی.",size=8.5,color=GREY)
    heading(doc,"۱۳. منابع و بازتولید")
    for item in [
        "بهاره، ایمیل ۳۰ سپتامبر ۲۰۲۶: AI_Balanced_Panel (1).xlsx، AI_Balanced_Panel_Dictionary (1).xlsx و فایل روش تحقیق همراه.",
        "بانک جهانی، کدهای TX.VAL.TECH.MF.ZS، NY.GDP.MKTP.KD.ZG و SL.UEM.TOTL.ZS؛ تاریخ برداشت نسخه اصلی در داده اولیه نامشخص است.",
        "Arellano, M. & Bond, S. (1991). Some Tests of Specification for Panel Data. Review of Economic Studies, 58(2), 277–297.",
        "Blundell, R. & Bond, S. (1998). Initial Conditions and Moment Restrictions in Dynamic Panel Data Models. Journal of Econometrics, 87(1), 115–143.",
        "Roodman, D. (2009). How to do xtabond2: An Introduction to Difference and System GMM in Stata. Stata Journal, 9(1), 86–136.",
        "Nickell, S. (1981). Biases in Dynamic Models with Fixed Effects. Econometrica, 49(6), 1417–1426."
    ]: bullet(doc,item)
    heading(doc,"پیوست پ. اختلاف‌های ثبت‌شده با نسخه فعلی بانک جهانی",level=2)
    wd=[r for r in csv_rows("WDI_REFERENCE_ROW_COMPARISON_20261017.csv")
        if r["source_col"]=="HighTech_Exports" and r["equal_to_0.001"]=="False"]
    if len(wd)!=17: raise RuntimeError("Unexpected official WDI discrepancy count")
    tab(doc,["کشور","سال","مقدار فایل بهاره","مرجع WDI فعلی","قدر مطلق اختلاف"],[
        [r["ISO3"],num(r["Year"]),fnum(r["original_supplied_value"]),
         fnum(r["wdi_reference_value"]),fnum(r["absolute_deviation"])] for r in wd],font_size=7.9)
    add_p(doc,"همه ۱۷ مورد اختلاف در شاخص TX.VAL.TECH.MF.ZS مشاهده شده‌اند. تاریخ آخرین به‌روزرسانی مرجع ۸ اکتبر ۲۰۲۶ است؛ این جدول درباره منشأ اختلاف قضاوت نمی‌کند و مبنای تخمین همچنان مقادیر اصلی بهاره است.",size=9,color=GREY)

    add_p(doc,"پیوست‌های داده، do-fileها، فایل‌های خروجی واقعی Stata، آزمون‌های تشخیصی و گزارش کامل ممیزی در مخزن AI-Innovation-GMM، شاخه feat/stata-estimation-audit-20261017 نگهداری می‌شوند. فایل اصلی داده بدون تغییر حفظ شده و برای ادعاهای جدید از داده جایگزین استفاده نشده است.",size=9)
    add_p(doc,"حکم نهایی کنترل کیفیت: گزارش پژوهش براساس داده‌های ارائه‌شده توسط استاد آماده تحویل و بازبینی اوست؛ نتیجه‌گیری صرفاً ارتباطی و اکتشافی است و اثبات علّیت از آزمون‌های انجام‌شده حاصل نشده است.",size=10,bold=True,color=BLUE)
    output=DIST/"AI_GMM_Professor_Review_FA.docx"
    doc.save(output)
    print("DOCX_CREATED",output,output.stat().st_size)
    return output

if __name__=="__main__":
    source=create_docx()
    cmd=shutil.which("libreoffice") or shutil.which("soffice")
    if cmd:
        subprocess.run([cmd,"-env:UserInstallation=file:///tmp/lo_ai_professor_persist","--headless","--convert-to","pdf","--outdir",str(DIST),str(source)],check=True,timeout=150)
        pdf=source.with_suffix(".pdf")
        if not pdf.exists():raise RuntimeError("LibreOffice returned but PDF absent")
        print("PDF_CREATED",pdf,pdf.stat().st_size)
    else:
        print("NO_LIBREOFFICE: DOCX only")
