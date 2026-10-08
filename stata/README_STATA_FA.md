# راهنمای اجرای Stata

**برای شروع از فایل اصلی [STATA_START_HERE_FA.md](../STATA_START_HERE_FA.md) استفاده کن.**

در این نسخه ۸ مدل (صادرات و بیکاری، با/بدون ۲۰۲۴، Difference و System) جداگانه اجرا می‌شوند و هر مدل لاگ خاص خود با نام `outputs/AI_<Outcome>_<Year>_<method>.log` دارد. جدول واقعی در `outputs/stata_model_summary.csv` ذخیره می‌شود. فایل‌های قدیمی `stata_hightech_models.log` دیگر معیار این بسته نیستند. قبل از دریافت لاگ Stata مجاز، تمام آزمون‌های آن اجرا نشده‌اند.

آزمون Difference-in-Hansen فقط در خروجی System GMM قابل بررسی است و صرف وجود دستور `split` به معنی پذیرش آن نیست. اگر وضعیت `INVALID_*` یا `EXECUTION_FAILED` ثبت شد، مدل را معتبر معرفی نکن.
