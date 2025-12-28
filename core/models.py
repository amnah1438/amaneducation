from django.db import models


class SchoolSettings(models.Model):
    """
    إعدادات المدرسة العامة (لوحة الإدارة):
    - اسم المنصة
    - شعارات الوزارة والمدرسة
    - اسم المديرة
    - بيانات الديباجة الرسمية للتقارير
    """

    platform_name = models.CharField(
        max_length=200,
        default="آمنه مالح العنزي",
        verbose_name="اسم المنصة"
    )

    principal_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="اسم المديرة"
    )

    ministry_logo = models.ImageField(
        upload_to="logos/",
        blank=True,
        null=True,
        verbose_name="شعار وزارة التعليم"
    )

    school_logo = models.ImageField(
        upload_to="logos/",
        blank=True,
        null=True,
        verbose_name="شعار المدرسة"
    )

    header_line_1 = models.CharField(
        max_length=200,
        default="المملكة العربية السعودية",
        verbose_name="سطر الديباجة 1"
    )

    header_line_2 = models.CharField(
        max_length=200,
        default="وزارة التعليم",
        verbose_name="سطر الديباجة 2"
    )

    header_line_3 = models.CharField(
        max_length=300,
        default="الإدارة العامة للتعليم بمنطقة الحدود الشمالية",
        verbose_name="سطر الديباجة 3"
    )

    header_line_4 = models.CharField(
        max_length=300,
        default="الثانوية الثالثة عشر بعرعر",
        verbose_name="سطر الديباجة 4"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث"
    )

    class Meta:
        verbose_name = "إعدادات المدرسة"
        verbose_name_plural = "إعدادات المدرسة"

    def __str__(self):
        return self.platform_name
