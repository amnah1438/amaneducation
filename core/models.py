from django.db import models

class SchoolSettings(models.Model):
    """
    إعدادات المدرسة العامة (لوحة الإدارة):
    تحتوي على الهوية البصرية، بيانات الديباجة الرسمية، وصلاحيات عرض الإحصاءات للمشرفات.
    """

    # --- القسم الأول: هوية المنصة ---
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

    platform_vision = models.TextField(
        blank=True, 
        verbose_name="رؤية المنصة (تظهر في التذييل)"
    )

    # --- القسم الثاني: الشعارات والألوان ---
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

    primary_color = models.CharField(
        max_length=7, 
        default="#E6E6FA", 
        verbose_name="اللون الأساسي (لافندر)"
    )

    # --- القسم الثالث: الديباجة الرسمية للتقارير ---
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

    # --- القسم الرابع: التحكم في العرض للمشرفات ---
    show_stats_to_public = models.BooleanField(
        default=True, 
        verbose_name="إظهار الإحصاءات العامة للمشرفات"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث"
    )

    class Meta:
        verbose_name = "1. إعدادات الهوية الرسمية"
        verbose_name_plural = "1. إعدادات الهوية الرسمية"

    def __str__(self):
        return self.platform_name

    def save(self, *args, **kwargs):
        if not self.pk and SchoolSettings.objects.exists():
            self.pk = SchoolSettings.objects.first().pk
        return super(SchoolSettings, self).save(*args, **kwargs)


# --- القسم الجديد: المهارات والدروس (لتطبيق التبويبات التفاعلية) ---

class Skill(models.Model):
    """
    هذا الموديل يمثل البطاقات التي ستظهر عند الضغط على (كمي، لفظي، رياضيات، إلخ)
    """
    CATEGORY_CHOICES = [
        ('QUANT', 'قسم القدرات - كمي'),
        ('VERBAL', 'قسم القدرات - لفظي'),
        ('MATH', 'قسم التحصيلي - رياضيات'),
        ('BIO', 'قسم التحصيلي - أحياء'),
        ('CHEM', 'قسم التحصيلي - كيمياء'),
        ('PHYS', 'قسم التحصيلي - فيزياء'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان المهارة/الدرس")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, verbose_name="القسم التابع له")
    icon_image = models.ImageField(upload_to="skills_icons/", blank=True, null=True, verbose_name="أيقونة المهارة (اختياري)")
    short_description = models.CharField(max_length=300, blank=True, verbose_name="وصف مختصر للبطاقة")
    
    # لون البطاقة (مثل اللون الأخضر)
    card_color = models.CharField(max_length=7, default="#2D5A27", verbose_name="لون البطاقة")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "2. إضافة مهارة/درس"
        verbose_name_plural = "2. إضافة مهارات ودروس"

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"