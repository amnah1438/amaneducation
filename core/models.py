from django.db import models


class SchoolSettings(models.Model):
    """
    إعدادات المدرسة العامة (لوحة الإدارة):
    - اسم المنصة
    - شعارات الوزارة والمدرسة
    - اسم المديرة
    - بيانات الديباجة الرسمية للتقارير
    """
    platform_name = models.CharField(max_length=200, default="آمنه مالح العنزي")
    principal_name = models.CharField(max_length=200, blank=True, default="")

    ministry_logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    school_logo = models.ImageField(upload_to="logos/", blank=True, null=True)

    header_line_1 = models.CharField(max_length=200, default="المملكة العربية السعودية")
    header_line_2 = models.CharField(max_length=200, default="وزارة التعليم")
    header_line_3 = models.CharField(max_length=300, default="الإدارة العامة للتعليم بمنطقة الحدود الشمالية")
    header_line_4 = models.CharField(max_length=300, default="الثانوية الثالثة عشر بعرعر")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.platform_name
