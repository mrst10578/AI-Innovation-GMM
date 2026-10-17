# راهنمای اجرای واقعی Stata

این بسته برای پژوهش سرمایه‌گذاری و پتنت هوش مصنوعی است و از مطالعه اقتصاد دیجیتال مستقل است.

۱. از **ریشه ریپو** اجرا کنید. نیاز به Stata دارای مجوز و افزونه `xtabond2` دارید.

۲. اگر `data/processed/stata_ready.dta` موجود نیست، قبل از ورود به استاتا با Python اجرا کنید:

```bash
python -m pip install -r requirements-python.txt
python -m src.python.preflight
python -m src.python.to_stata
```

۳. داخل Stata:

```stata
cd "PATH_TO_CLONED_AI-Innovation-GMM"
ssc install xtabond2, replace
do "stata/RUN_ALL.do"
```

اگر اینترنت در Stata در دسترس نیست، xtabond2 را از منبع معتبر SSC به روش آفلاین نصب کنید. اجرای `RUN_ALL.do` هیچ نتیجه‌ای را از پیش فرض نمی‌کند.

۴. خروجی‌های واقعی در `outputs/stata/` تولید می‌شوند: `00_master.log`، `hightech.log`، `unemployment.log` و فایل‌های تخمین `.ster` برای مدل‌های موفق. گزارش‌های چهار حالت GMM (تفاضلی/سیستمی، یک‌مرحله‌ای/دو‌مرحله‌ای) با و بدون ۲۰۲۴ را بررسی کنید.

**اخطار روش‌شناختی:** ۳۰ کشور و ۹ سال برای GMM شکننده‌اند. پیش از اعلام اعتبار مدل، تعداد ابزارها، AR(2)، Hansen/Sargan و فرض‌های ابزارهای سطح را بررسی کنید. در صورت رد فرض‌ها، مدل را نامعتبر گزارش کنید. نبود خطای نرم‌افزاری، تأیید علمی نیست. تبدیل داده به `.dta` به معنای اجرای Stata نیست.
