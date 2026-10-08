# اجرای واقعی Stata صبح روی لپ‌تاپ
۱. از ریشهٔ همین ریپو کار کن. Stata باید نسخهٔ مجاز و فعال باشد؛ در این مرحله هیچ اجرای Stata تأیید نشده است.

۲. اگر مخزن را clone کردی، فایل `data/raw/AI_Balanced_Panel (1).xlsx` در آن قرار دارد. اگر نسخهٔ DTA را از artifact دریافت کردی، آن را در `data/processed/stata_ready.dta` قرار بده. داده از پروژهٔ دیگری نباشد.

۳. در Stata از File > Change Working Directory، پوشهٔ ریشهٔ `AI-Innovation-GMM` را انتخاب کن، سپس:
```stata
capture which xtabond2
ssc install xtabond2, replace
do "stata/RUN_ALL.do"
```

۴. `outputs/stata_preflight.log`، `outputs/stata_hightech_models.log` و `outputs/stata_unemployment_models.log` را باز کن. در هر یک `number of instruments`، `groups`، `Hansen`، `Sargan`، `AR(1)`، `AR(2)` و `Difference-in-Hansen` را از خروجی **واقعی** بخوان. خطاها را نیز کپی کن.

۵. دقت کن `p>0.05` در Hansen تأیید نهایی ابزار نیست. هر آزمون با df صفر یا p نامعتبر را «نامعتبر» ثبت کن. پایایی نتیجه در ۲۰۲۳/۲۰۲۴ را بررسی کن. `split` در `gmmstyle` طبق مستندات رسمی xtabond2 برای آزمون زیرمجموعه ابزارها استفاده شده، نه گزینهٔ `diff` ادعاشده در تصویر.

۶. در صورت خطای `xtabond2 unrecognized` اینترنت و SSC را بررسی کن؛ اگر فایل DTA نبود، اسکریپت Excel اصلی را مستقیماً وارد می‌کند. اگر تغییر نام متغیر یا نسخهٔ Stata مشکل داشت، **هیچ نتیحه‌ای را دستی بساز**؛ لاگ را برای اصلاح نگه‌دار.

**محدودیت اجرایی:** کدهای DO در این ریپو آمادهٔ اجرای واقعی هستند، ولی تا زمانی که شخص دارای Stata آنها را روی نسخهٔ واقعی آزمایش نکند، syntax و آماره‌های نرم‌افزار Stata «تأییدشده» نیستند. اختلاف Stata و R/gretl به‌معنای خطای یکی از آنها نیست؛ ماتریس ابزار و برآوردگرها باید مقایسه شوند.
