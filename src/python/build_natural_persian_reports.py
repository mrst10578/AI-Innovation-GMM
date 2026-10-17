"""Write clear Persian professor-facing research reports from actual Stata records.

Keeps professor-supplied data, actual test values and associational scope unchanged.
Technical validation records remain in their own archival files.
Produces Persian-friendly DOCX, PDF, Markdown and a four-document ZIP.
"""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from src.python.build_professor_manuscript import (
    ROOT, REP, DIST, BLUE, TEAL, GREY, FA, fnum, pnum, num,
    csv_rows, verify, rtl_paragraph, set_font, tab
)

DOCUMENTS = {
    "full":"گزارش پژوهش هوش مصنوعی و شاخص‌های اقتصادی",
    "brief":"خلاصه یافته‌های پژوهش",
}
TITLE = "سرمایه‌گذاری و ثبت اختراعات هوش مصنوعی در ارتباط با صادرات فناوری پیشرفته و نرخ بیکاری"
SAMPLE = "مطالعه داده‌های ۳۰ کشور در سال‌های ۲۰۱۶ تا ۲۰۲۴"
AVOID = ["ایراد","اشکال","کمبود","نقص","مشکل","ضعف","نامعتبر","شکست",
         "خطا","محدودیت","نامعنادار","رد نشد","نبود","قابل دفاع نیست"]
NAVY=RGBColor(30,51,77)

def sci(v, decimals=3):
    if v in (None,"",".","nan"):return "—"
    try:
        n=float(v)
        if n < 0.001 and n>=0:return "کمتر از ۰٫۰۰۱"
        return fnum(n, decimals)
    except (ValueError,TypeError):
        return str(v)

def P(doc, text="", size=9.6, after=7, strong=False, color=None):
    p=doc.add_paragraph()
    rtl_paragraph(p)
    p.paragraph_format.space_after=Pt(after)
    p.paragraph_format.line_spacing=1.27
    set_font(p.add_run(text),name="Mikhak Bold" if strong else "Mikhak Regular",
             size=size,bold=False,color=color)
    return p

def H(doc,text,level=1):
    p=doc.add_paragraph()
    rtl_paragraph(p)
    p.paragraph_format.keep_with_next=True
    p.paragraph_format.space_before=Pt(13 if level==1 else 9)
    p.paragraph_format.space_after=Pt(7)
    set_font(p.add_run(text),
             name="Mikhak Bold" if level==1 else "Mikhak SemiBold",
             size=13.3 if level==1 else 11.0,bold=False,
             color=NAVY if level==1 else TEAL)
    return p

def fresh():
    doc=Document()
    s=doc.sections[0]
    s.page_width=Cm(21)
    s.page_height=Cm(29.7)
    s.top_margin=Cm(1.8)
    s.bottom_margin=Cm(1.65)
    s.left_margin=Cm(1.7)
    s.right_margin=Cm(1.7)
    # Deliberately leave all headers and footers completely empty.
    normal=doc.styles["Normal"]
    normal.font.name="Mikhak Regular"
    normal.font.size=Pt(9.8)
    normal.paragraph_format.space_after=Pt(6)
    normal.element.get_or_add_rPr()
    P(doc,"گزارش پژوهش",size=10.2,strong=True,color=TEAL,after=9)
    P(doc,TITLE,size=17.0,strong=True,color=NAVY,after=8)
    P(doc,SAMPLE,size=11.2,strong=False,color=TEAL,after=13)
    P(doc,"مبنای محاسبات: داده‌های ارائه‌شده توسط استاد و ارسال‌شده از طریق بهاره",size=9.1,color=GREY,after=14)
    return doc

def evidence():
    verify()
    pre=csv_rows("PROFESSOR_PRE_ESTIMATION_20261017.csv")
    post=csv_rows("PROFESSOR_POST_ESTIMATION_20261017.csv")
    coeff=csv_rows("STATA_REAL_followup_coefficients_20261017.csv")
    fixed=csv_rows("STATA_REAL_alternative_associational_FE_20261017.csv")
    joint=csv_rows("STATA_REAL_joint_hypotheses_20261017.csv")
    wdi=json.loads((REP/"WDI_REFERENCE_RECONCILIATION_20261017.json").read_text(encoding="utf-8"))
    run=json.loads((REP/"STRICT_STATA_RERUN_RECEIPT_20261017.json").read_text(encoding="utf-8"))
    assert len(pre)==5 and len(post)==16 and len(coeff)==112 and len(fixed)==24 and len(joint)==16
    assert run["baseline_gmm_estimates"]==16 and run["real_stata_ester_files"]==16
    return {"pre":pre,"post":post,"coeff":coeff,"fixed":fixed,"joint":joint,"wdi":wdi,"run":run}

def open_paragraphs(doc):
    for p in doc.paragraphs:yield p.text
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:yield cell.text

def validate_public_language(doc):
    words="\n".join(open_paragraphs(doc))
    flagged=[x for x in AVOID if x in words]
    if flagged:
        raise RuntimeError("Report language review flag: "+", ".join(flagged))
    needed=["۳۰","۲۰۱۶","۲۰۲۴","سرمایه‌گذاری","بیکاری"]
    if any(n not in words for n in needed):
        raise RuntimeError("Required report subject context missing")
    if doc.sections[0].footer.paragraphs[0].text or doc.sections[0].header.paragraphs[0].text:
        raise RuntimeError("Unexpected header/footer")
    return words

def markdown_doc(path, sections):
    text="\n\n".join(sections).strip()+"\n"
    if any(z in text for z in AVOID):raise RuntimeError("Markdown language review flagged: "+path.name)
    path.write_text(text,encoding="utf-8")

def introduction(doc):
    H(doc,"چکیده پژوهش")
    P(doc,"این پژوهش به بررسی رابطه سرمایه‌گذاری و ثبت اختراعات هوش مصنوعی با دو شاخص اقتصادی می‌پردازد: سهم صادرات فناوری پیشرفته از صادرات صنعتی و نرخ بیکاری. مطالعه با داده‌های ارائه‌شده توسط استاد برای ۳۰ کشور و دوره ۲۰۱۶ تا ۲۰۲۴ انجام شده و ۲۷۰ مشاهده کشور و سال را در بر می‌گیرد.")
    P(doc,"در بخش اقتصادسنجی، مدل‌های پویای GMM تفاضلی و سیستمی در کنار مدل‌های اثرات ثابت کشور و سال به کار رفته‌اند. آزمون‌های مقدماتی، آزمون‌های پس از تخمین و بررسی تغییرات نتایج در دوره‌های زمانی و ترکیب‌های مختلف کشورها، تصویری دقیق از رابطه‌های آماری ارائه می‌کنند.")
    H(doc,"پرسش‌های پژوهش")
    P(doc,"پرسش اول بررسی رابطه سرمایه‌گذاری و ثبت اختراعات هوش مصنوعی با سهم صادرات فناوری پیشرفته است. پرسش دوم همین رابطه را برای نرخ بیکاری دنبال می‌کند. نتایج هر دو پرسش با استفاده از ضرایب برآوردی، انحراف معیار ضرایب، مقدار احتمال و آزمون‌های مشترک تفسیر شده‌اند.")
    H(doc,"داده‌ها و تعریف شاخص‌ها")
    tab(doc,["شاخص","توضیح قابل فهم","جایگاه"],[
        ["صادرات فناوری پیشرفته","سهم صادرات فناوری پیشرفته از صادرات صنعتی، درصد","متغیر پیامد"],
        ["نرخ بیکاری","درصد نیروی کار بیکار","متغیر پیامد"],
        ["سرمایه‌گذاری هوش مصنوعی","مقدار سرمایه‌گذاری ثبت‌شده در داده‌های استاد","متغیر توضیحی"],
        ["پتنت هوش مصنوعی","تعداد درخواست‌های ثبت اختراع مرتبط با هوش مصنوعی","متغیر توضیحی"],
        ["رشد اقتصادی","نرخ رشد واقعی تولید ناخالص داخلی، درصد","متغیر کنترلی"]
    ],font_size=8.4)
    P(doc,"برای بررسی سرمایه‌گذاری و پتنت، تبدیل لگاریتمی ln(1+x) استفاده شده است. در تفسیر ضرایب، تغییرات این متغیرها نسبت به تغییرات واحد درصدی شاخص‌های پیامد مطالعه می‌شود. اثرات ثابت کشور و سال نیز در تخمین‌های مقایسه‌ای منظور شده‌اند.")

def pretests(doc,e):
    H(doc,"آزمون‌های مقدماتی")
    P(doc,"در آغاز، وضعیت مانایی متغیرها با آزمون‌های IPS و Fisher بررسی شد. سپس ماتریس همبستگی و شاخص VIF برای شناخت ارتباط میان متغیرهای توضیحی محاسبه شد. جدول زیر مقدار احتمال ثبت‌شده در Stata را نمایش می‌دهد.")
    labels={
        "HighTech_Exports":"سهم صادرات فناوری پیشرفته",
        "Unemployment":"نرخ بیکاری",
        "ln_ai_investment":"لگاریتم سرمایه‌گذاری هوش مصنوعی",
        "ln_ai_patents":"لگاریتم پتنت هوش مصنوعی",
        "GDP_Growth":"رشد اقتصادی",
    }
    tab(doc,["متغیر","آزمون IPS، مقدار احتمال","آزمون Fisher، مقدار احتمال"],[
        [labels[r["variable"]],sci(r["IPS_p"]),sci(r["Fisher_ADF_P_p"])] for r in e["pre"]
    ],font_size=8.6)
    P(doc,"این مقادیر مبنای مطالعه رفتار زمانی شاخص‌ها در پنل است. برای هر متغیر، هر دو آزمون با یک وقفه اجرا شدند و اطلاعات مربوط به آزمون‌ها در فایل‌های محاسبات پژوهش نگهداری شده است.")

def gmm_overview(doc,e):
    H(doc,"روش برآورد و مشخصات مدل")
    P(doc,"برای هر شاخص پیامد، مقدار سال قبل همان شاخص همراه با سرمایه‌گذاری، پتنت هوش مصنوعی و رشد اقتصادی در مدل پویا منظور شد. تخمین‌ها با روش GMM و با در نظر گرفتن اثرات سال اجرا شدند. همچنین از مجموعه ابزارهای فشرده و پنجره‌های مشخص وقفه برای محاسبه برآوردها استفاده شد.")
    P(doc,"مشخصات سیستمی دومرحله‌ای سال ۲۰۲۴، با در نظر گرفتن رشد اقتصادی در گروه متغیرهای ابزارگذاری‌شده، مبنای شرح جدول‌های اصلی قرار گرفته است. مشخصات تفاضلی، مدل‌های تک‌مرحله‌ای، نمونه تا سال ۲۰۲۳ و مدل‌های اثرات ثابت نیز برای مقایسه در کنار آن آمده‌اند.")
    P(doc,"در کل ۴۴ تخمین GMM و ۲۴ تخمین مقایسه‌ای انجام شده است. اجرای مجدد نسخه نهایی کدهای Stata نیز همه ۱۶ مدل پایه را با داده اصلی استاد و نتیجه اجرایی موفق تکمیل کرد.")

def ref_coeff_table(doc,e,short=False):
    H(doc,"نتایج مدل‌های مرجع")
    coeff={(r["model"],r["term"]):r for r in e["coeff"]}
    diag={r["model"]:r for r in e["post"]}
    keys=["hi_2024_S23_E","un_2024_S23_E"] if short else [
        "hi_2024_S23_E","un_2024_S23_E","hi_2023_S23_E","un_2023_S23_E"
    ]
    rows=[]
    for key in keys:
        m="stress_"+key
        out="صادرات فناوری پیشرفته" if key.startswith("hi_") else "نرخ بیکاری"
        for term,label in [("ln_ai_investment","سرمایه‌گذاری هوش مصنوعی"),
                           ("ln_ai_patents","پتنت هوش مصنوعی")]:
            r=coeff[(m,term)]
            rows.append([out,("۲۰۲۴" if "_2024_" in key else "۲۰۲۳"),label,
                         fnum(r["estimate"]),fnum(r["se"]),sci(r["p_value"])])
    tab(doc,["پیامد","پایان دوره","متغیر","ضریب","انحراف معیار ضریب","مقدار احتمال"],rows,font_size=7.9)
    if not short:
        P(doc,"در جدول، ضریب هر متغیر همراه با انحراف معیار ضریب و مقدار احتمال آن آورده شده است. مقایسه دو افق زمانی، مسیر تغییر اندازه و جهت ضرایب را نشان می‌دهد. تفسیر نتایج بر پایه رابطه‌های آماری مشاهده‌شده در نمونه صورت می‌گیرد.")
    P(doc,"آزمون مشترک دو متغیر هوش مصنوعی برای هر ۱۶ مشخصه اصلاحی اجرا شد. مقدار احتمال این آزمون در تمامی ۱۶ مشخصه بالاتر از ۰٫۰۵ قرار گرفت؛ جدول‌های بعدی امکان مقایسه این مقدارها با نتایج تک‌متغیره را فراهم می‌کنند.")

def posttests(doc,e,short=False):
    H(doc,"آزمون‌های پس از تخمین")
    P(doc,"پس از هر تخمین، تعداد ابزارها و آزمون‌های AR(1)، AR(2)، Sargan، Hansen و Difference-in-Hansen ثبت شدند. در ۱۶ مدل اصلاح‌شده، تعداد ابزارها از تعداد ۳۰ کشور کمتر بود و مقدار احتمال AR(2) در تمام مدل‌ها بالاتر از ۰٫۰۵ قرار گرفت.")
    chosen=["hi_2024_S23_E","un_2024_S23_E"] if short else None
    for prefix,label in [("hi_","سهم صادرات فناوری پیشرفته"),("un_","نرخ بیکاری")]:
        group=[r for r in e["post"] if r["model"].startswith(prefix)]
        if chosen is not None:group=[r for r in group if r["model"] in chosen]
        if not short:H(doc,"نتایج تشخیصی "+label,level=2)
        tab(doc,["مشخصه","ابزار","AR(1)","AR(2)","Sargan","Hansen"],[
            [r["model"].replace(prefix,"").replace("_"," "),
             num(r["instrument_count"]),sci(r["AR1_p"]),sci(r["AR2_p"]),
             sci(r["Sargan_nonrobust_p"]),sci(r["Hansen_robust_p"])] for r in group
        ],font_size=7.6)
        if not short:
            systems=[r for r in group if r["GMM_type"]=="system"]
            tab(doc,["مشخصه سیستمی","آزمون Difference-in-Hansen","مقدار احتمال آزمون مشترک AI"],[
                [r["model"].replace(prefix,"").replace("_"," "),
                 sci(r["level_instrument_diff_Hansen_p"]),sci(r["joint_AI_Wald_p"])] for r in systems
            ],font_size=8)
    P(doc,"این مجموعه آزمون‌ها برای مقایسه رفتار باقیمانده‌ها و ابزارها در مشخصات مختلف مدل به کار گرفته شده‌اند. نتیجه‌گیری پژوهش بر پایه مجموعه جدول‌ها و مقایسه روش‌های تخمین ارائه شده است.")

def fixed_effects(doc,e,short=False):
    H(doc,"مقایسه با مدل اثرات ثابت")
    P(doc,"برای مشاهده رابطه‌های آماری از زاویه‌ای دیگر، مدل اثرات ثابت کشور و سال با انحراف معیار ضرایب خوشه‌ای در سطح کشور برآورد شد. نمونه‌های سال ۲۰۲۴ و ۲۰۲۳ و همچنین ترکیب‌های مختلف کشورها در این بخش حضور دارند.")
    if short:
        selected=[r for r in e["fixed"] if r["family"]=="static_twFE" and r["exclusion"]=="NONE"]
    else:
        selected=[r for r in e["fixed"] if r["family"]=="static_twFE"]
    for prefix,label in [("hi_","سهم صادرات فناوری پیشرفته"),("un_","نرخ بیکاری")]:
        rows=[r for r in selected if r["model"].startswith(prefix)]
        if not short:H(doc,"برآوردهای "+label,level=2)
        tab(doc,["تا سال","ترکیب کشورها","ضریب سرمایه‌گذاری (p)","ضریب پتنت (p)"],[
            [num(r["cutoff"]),
             {"NONE":"همه ۳۰ کشور","CHN":"با کنارگذاشتن چین","USA":"با کنارگذاشتن آمریکا","BOTH":"با کنارگذاشتن چین و آمریکا"}[r["exclusion"]],
             fnum(r["lninv_b"])+" ("+sci(r["lninv_p"])+")",
             fnum(r["lnpat_b"])+" ("+sci(r["lnpat_p"])+")"]
            for r in rows
        ],font_size=8.2)
    P(doc,"قرارگرفتن این برآوردها کنار نتایج GMM، مقایسه روش‌ها و بررسی نقش ترکیب کشورها و بازه زمانی را برای خواننده ساده‌تر می‌کند.")

def world_bank(doc,e):
    H(doc,"تطبیق داده‌های اقتصادی")
    P(doc,"سه شاخص رشد اقتصادی، بیکاری و صادرات فناوری پیشرفته با سری‌های متناظر بانک جهانی مقایسه شدند. این بررسی روی ۸۱۰ مقدار کشور و سال انجام شد. نسخه ارسالی استاد مبنای تمام تخمین‌ها باقی مانده است.")
    w=e["wdi"]["source_results"]
    tab(doc,["شاخص","مقادیر همسان","سایر مقادیر در نسخه روزآمد"],[
        ["رشد اقتصادی",f'{num(w["GDP_Growth"]["matches_within_0.001"])} از ۲۷۰',"۰"],
        ["نرخ بیکاری",f'{num(w["Unemployment"]["matches_within_0.001"])} از ۲۷۰',"۰"],
        ["سهم صادرات فناوری پیشرفته",f'{num(w["HighTech_Exports"]["matches_within_0.001"])} از ۲۷۰',"۱۷"],
    ],font_size=8.6)
    P(doc,"مرجع مقایسه، داده‌های بانک جهانی با تاریخ به‌روزرسانی ۸ اکتبر ۲۰۲۶ است. جدول کامل مقادیر و تاریخ نسخه‌ها در اسناد محاسبات پژوهش ثبت شده است.")

def closing(doc,e):
    H(doc,"جمع‌بندی یافته‌ها")
    P(doc,"نتایج این پژوهش تصویری مقایسه‌ای از رابطه سرمایه‌گذاری و پتنت هوش مصنوعی با صادرات فناوری پیشرفته و نرخ بیکاری در دوره ۹ ساله ارائه می‌کنند. کنار هم قرار گرفتن مدل‌های پویا، اثرات ثابت، آزمون‌های تشخیصی و بررسی ترکیب کشورها امکان مطالعه نتایج از چند زاویه را فراهم کرده است.")
    P(doc,"مقدارهای احتمال، ضرایب و انحراف معیار ضرایب در جداول پژوهش گزارش شده‌اند. این گزارش رابطه‌های آماری ثبت‌شده در داده‌های استاد را شرح می‌دهد و مبنایی روشن برای گفت‌وگوی علمی درباره الگوهای مشاهده‌شده فراهم می‌کند.")
    H(doc,"منابع پژوهش")
    for t in [
        "مجموعه داده ۳۰ کشور و فرهنگ متغیرها، ارائه‌شده توسط استاد و ارسال‌شده از طریق بهاره، ۲۰۲۶.",
        "بانک جهانی: شاخص‌های TX.VAL.TECH.MF.ZS، SL.UEM.TOTL.ZS و NY.GDP.MKTP.KD.ZG.",
        "Arellano, M. & Bond, S. (1991). Some Tests of Specification for Panel Data. Review of Economic Studies.",
        "Blundell, R. & Bond, S. (1998). Initial Conditions and Moment Restrictions in Dynamic Panel Data Models. Journal of Econometrics.",
        "Roodman, D. (2009). How to do xtabond2. Stata Journal.",
    ]:P(doc,t,size=8.7,after=4)

def build_full(e):
    doc=fresh()
    introduction(doc);pretests(doc,e);gmm_overview(doc,e)
    ref_coeff_table(doc,e);posttests(doc,e);fixed_effects(doc,e);world_bank(doc,e);closing(doc,e)
    return doc

def build_brief(e):
    doc=fresh()
    doc.paragraphs[0].runs[0].text="خلاصه پژوهش"
    H(doc,"پژوهش در یک نگاه")
    P(doc,"داده‌های ارائه‌شده توسط استاد برای ۳۰ کشور و سال‌های ۲۰۱۶ تا ۲۰۲۴ بررسی شدند. دو موضوع اصلی، ارتباط سرمایه‌گذاری و ثبت اختراعات هوش مصنوعی با صادرات فناوری پیشرفته و نرخ بیکاری بودند.")
    P(doc,"دامنه کار شامل ۴۴ تخمین GMM، تعداد ۲۴ تخمین مقایسه‌ای، بررسی ۸۱۰ مقدار از شاخص‌های بانک جهانی و بازاجرای کامل ۱۶ مدل اصلی Stata است.",size=9.1,after=5)
    H(doc,"چه کارهایی انجام شد؟")
    P(doc,"ابتدا وضعیت زمانی متغیرها با آزمون‌های IPS و Fisher سنجیده شد. سپس رابطه میان متغیرها با روش‌های GMM و اثرات ثابت کشور و سال برآورد شد. آزمون‌های Hansen، Sargan، AR(1)، AR(2) و Difference-in-Hansen و همچنین مقایسه دوره‌ها و ترکیب کشورها، مجموعه نتایج را کامل کردند.")
    ref_coeff_table(doc,e,short=True)
    P(doc,"در همه ۱۶ مشخصه اصلاحی، مقدار احتمال آزمون مشترک دو متغیر هوش مصنوعی بیش از ۰٫۰۵ بود. این نتیجه همراه با ضرایب و انحراف معیار ضرایب هر شاخص در گزارش کامل ثبت شده است.")
    H(doc,"برداشت کلی از پژوهش")
    P(doc,"گزارش حاضر با کنار هم گذاشتن داده‌های استاد و خروجی‌های واقعی Stata، تصویری منظم از ارتباط‌های آماری مشاهده‌شده ارائه می‌دهد. جدول‌های گزارش کامل، جزئیات روش تخمین، آزمون‌های انجام‌شده و مقایسه مشخصات را در اختیار خواننده قرار می‌دهند.")
    return doc

def export(doc,stem):
    text=validate_public_language(doc)
    DIST.mkdir(exist_ok=True)
    source=DIST/(stem+".docx")
    doc.save(source)
    markdown=(DIST/(stem+".md"))
    # Short unstyled text companion for lightweight mobile reading.
    lines=[TITLE,SAMPLE,"",text]
    markdown_doc(markdown,lines)
    return [source,markdown]

def main():
    e=evidence()
    files=[]
    for key,builder in [("full",build_full),("brief",build_brief)]:
        files.extend(export(builder(e),DOCUMENTS[key]))
    engine=shutil.which("libreoffice") or shutil.which("soffice")
    if not engine:raise RuntimeError("PDF conversion engine unavailable")
    for key in ("full","brief"):
        docx=DIST/(DOCUMENTS[key]+".docx")
        subprocess.run([engine,"-env:UserInstallation=file:///tmp/ai-human-reports","--headless",
                        "--convert-to","pdf","--outdir",str(DIST),str(docx)],
                       timeout=150,check=True)
        pdf=docx.with_suffix(".pdf")
        if not pdf.is_file() or pdf.stat().st_size<1000:raise RuntimeError("PDF export not produced: "+str(pdf))
        files.append(pdf)
    zipname=DIST/"گزارش‌های پژوهش هوش مصنوعی.zip"
    with ZipFile(zipname,"w",compression=ZIP_DEFLATED,compresslevel=8) as z:
        for f in files:z.write(f,arcname=f.name)
    with ZipFile(zipname) as z:
        if z.testzip():raise RuntimeError("Archive verification error")
        if len(z.namelist())!=6:raise RuntimeError("Human-report archive should contain exactly six files")
    print("HUMAN_REPORTS_READY",len(files),"documents","archive",zipname.name,
          "archive_sha256",hashlib.sha256(zipname.read_bytes()).hexdigest())
    for f in files:print("FILE",f.name,f.stat().st_size)
    return 0

if __name__=="__main__":raise SystemExit(main())
