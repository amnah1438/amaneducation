from django.db import models

class SchoolSettings(models.Model):
    # --- القسم الأول: هوية المنصة ---
    platform_name = models.CharField(max_length=200, default="آمنه مالح العنزي", verbose_name="اسم المنصة")
    principal_name = models.CharField(max_length=200, blank=True, default="", verbose_name="اسم المديرة")
    developer_name = models.CharField(max_length=200, default="آمنه مالح العنزي", verbose_name="اسم مبرمجة المنصة")
    platform_vision = models.TextField(blank=True, verbose_name="رؤية المنصة (تظهر في التذييل)")

    # --- القسم الثاني: الشعارات والألوان ---
    ministry_logo = models.ImageField(upload_to="logos/", blank=True, null=True, verbose_name="شعار وزارة التعليم")
    school_logo = models.ImageField(upload_to="logos/", blank=True, null=True, verbose_name="شعار المدرسة")
    primary_color = models.CharField(max_length=7, default="#E6E6FA", verbose_name="اللون الأساسي (لافندر)")

    # --- القسم الثالث: الديباجة الرسمية ---
    header_line_1 = models.CharField(max_length=200, default="المملكة العربية السعودية", verbose_name="سطر الديباجة 1")
    header_line_2 = models.CharField(max_length=200, default="وزارة التعليم", verbose_name="سطر الديباجة 2")
    header_line_3 = models.CharField(max_length=300, default="الإدارة العامة للتعليم بمنطقة الحدود الشمالية", verbose_name="سطر الديباجة 3")
    header_line_4 = models.CharField(max_length=300, default="الثانوية الثالثة عشر بعرعر", verbose_name="سطر الديباجة 4")

    show_stats_to_public = models.BooleanField(default=True, verbose_name="إظهار الإحصاءات العامة للمشرفات")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "1. إعدادات الهوية الرسمية"
        verbose_name_plural = "1. إعدادات الهوية الرسمية"

    def __str__(self):
        return self.platform_name

    def save(self, *args, **kwargs):
        if not self.pk and SchoolSettings.objects.exists():
            self.pk = SchoolSettings.objects.first().pk
        return super(SchoolSettings, self).save(*args, **kwargs)


# --- تعديل قسم المهارات لدعم المعلمات المتعددات ---

class Teacher(models.Model):
    """ موديل جديد لتعريف أسماء المعلمات """
    name = models.CharField(max_length=200, verbose_name="اسم المعلمة")
    
    class Meta:
        verbose_name = "3. أسماء المعلمات"
        verbose_name_plural = "3. أسماء المعلمات"

    def __str__(self):
        return self.name

class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('كمي', 'قسم القدرات - كمي'), # عدلت الرموز للعربية لتطابق لوحة الإدارة عندك
        ('لفظي', 'قسم القدرات - لفظي'),
        ('رياضيات', 'قسم التحصيلي - رياضيات'),
        ('أحياء', 'قسم التحصيلي - أحياء'),
        ('كيمياء', 'قسم التحصيلي - كيمياء'),
        ('فيزياء', 'قسم التحصيلي - فيزياء'),
    ]

    title = models.CharField(max_length=200, verbose_name="عنوان المهارة/الدرس")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="القسم التابع له")
    
    # التعديل هنا: حقل يسمح باختيار أكثر من معلمة
    teachers = models.ManyToManyField(Teacher, blank=True, verbose_name="المعلمات المسؤولات")
    
    icon_image = models.ImageField(upload_to="skills_icons/", blank=True, null=True, verbose_name="أيقونة المهارة (اختياري)")
    short_description = models.CharField(max_length=300, blank=True, verbose_name="وصف مختصر للبطاقة")
    card_color = models.CharField(max_length=7, default="#2D5A27", verbose_name="لون البطاقة")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "2. إضافة مهارة/درس"
        verbose_name_plural = "2. إضافة مهارات ودروس"

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"