from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from cloudinary.models import CloudinaryField

class SchoolSettings(models.Model):
    platform_name = models.CharField(max_length=200, default="آمنه مالح العنزي", verbose_name="اسم المنصة")
    principal_name = models.CharField(max_length=200, blank=True, default="", verbose_name="اسم المديرة")
    developer_name = models.CharField(max_length=200, default="آمنه مالح العنزي", verbose_name="اسم مبرمجة المنصة")
    platform_vision = models.TextField(blank=True, verbose_name="رؤية المنصة (تظهر في التذييل)")
    ministry_logo = CloudinaryField('شعار وزارة التعليم', folder='logos', blank=True, null=True)
    school_logo = CloudinaryField('شعار المدرسة', folder='logos', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#E6E6FA", verbose_name="اللون الأساسي (لافندر)")
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

    @property
    def ministry_logo_url(self):
        if self.ministry_logo:
            from cloudinary.utils import cloudinary_url
            val = str(self.ministry_logo)
            if val.startswith('http'):
                return val
            url, _ = cloudinary_url(val)
            return url or ''
        return ''

    @property
    def school_logo_url(self):
        if self.school_logo:
            from cloudinary.utils import cloudinary_url
            val = str(self.school_logo)
            if val.startswith('http'):
                return val
            url, _ = cloudinary_url(val)
            return url or ''
        return ''

    def save(self, *args, **kwargs):
        if not self.pk and SchoolSettings.objects.exists():
            self.pk = SchoolSettings.objects.first().pk
        return super(SchoolSettings, self).save(*args, **kwargs)


class Teacher(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم المعلمة")
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name="core_teacher_profile", verbose_name="حساب المستخدم المرتبط"
    )

    class Meta:
        verbose_name = "3. أسماء المعلمات"
        verbose_name_plural = "3. أسماء المعلمات"

    def __str__(self):
        return self.name


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('كمي', 'قسم القدرات - كمي'),
        ('لفظي', 'قسم القدرات - لفظي'),
        ('رياضيات', 'قسم التحصيلي - رياضيات'),
        ('أحياء', 'قسم التحصيلي - أحياء'),
        ('كيمياء', 'قسم التحصيلي - كيمياء'),
        ('فيزياء', 'قسم التحصيلي - فيزياء'),
    ]
    title = models.CharField(max_length=200, verbose_name="عنوان المهارة/الدرس")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="القسم التابع له")
    teachers = models.ManyToManyField(Teacher, blank=True, verbose_name="المعلمات المسؤولات")
    content_text = RichTextUploadingField(
        config_name='scientific_editor', blank=True, null=True,
        verbose_name="شرح الدرس (كتابة)"
    )
    video_url = models.URLField(blank=True, verbose_name="رابط فيديو (YouTube/Drive)")
    pdf_file = CloudinaryField('ملف PDF للشرح', resource_type='raw', folder='skills_pdf', blank=True, null=True)
    image_explainer = CloudinaryField('صورة توضيحية للشرح', folder='skills_images', blank=True, null=True)
    icon_image = CloudinaryField('أيقونة المهارة', folder='skills_icons', blank=True, null=True)
    short_description = models.CharField(max_length=300, blank=True, verbose_name="وصف مختصر للبطاقة")
    card_color = models.CharField(max_length=7, default="#2D5A27", verbose_name="لون البطاقة")
    required_questions_count = models.PositiveIntegerField(default=10, verbose_name="عدد أسئلة الاختبار")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "2. إضافة مهارة/درس"
        verbose_name_plural = "2. إضافة مهارات ودروس"

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"


class Question(models.Model):
    TEST_TYPES = [('PRE', 'اختبار قبلي'), ('POST', 'اختبار بعدي')]
    CORRECT_CHOICES = [('A', 'خيار أ'), ('B', 'خيار ب'), ('C', 'خيار ج'), ('D', 'خيار د')]

    skill = models.ForeignKey(Skill, related_name='questions', on_delete=models.CASCADE, verbose_name="المهارة/الدرس")
    test_type = models.CharField(max_length=4, choices=TEST_TYPES, default='POST', verbose_name="نوع الاختبار")
    question_text = RichTextUploadingField(config_name='scientific_editor', verbose_name="نص السؤال")
    option_a = RichTextUploadingField(config_name='scientific_editor', verbose_name="خيار (أ)")
    option_b = RichTextUploadingField(config_name='scientific_editor', verbose_name="خيار (ب)")
    option_c = RichTextUploadingField(config_name='scientific_editor', verbose_name="خيار (ج)")
    option_d = RichTextUploadingField(config_name='scientific_editor', verbose_name="خيار (د)")
    correct_answer = models.CharField(max_length=1, choices=CORRECT_CHOICES, verbose_name="الإجابة الصحيحة")
    feedback = RichTextUploadingField(config_name='scientific_editor', blank=True, null=True, verbose_name="التغذية الراجعة")

    class Meta:
        verbose_name = "سؤال"
        verbose_name_plural = "أسئلة الاختبارات"

    def __str__(self):
        from django.utils.html import strip_tags
        clean_text = strip_tags(self.question_text)
        return f"{self.get_test_type_display()} - {clean_text[:50]}"


class Profile(models.Model):
    USER_ROLES = [
        ('ADMIN', 'مديرة'),
        ('TEACHER', 'معلمة'),
        ('STUDENT', 'طالبة'),
    ]
    user = models.OneToOneField(
        'auth.User', on_delete=models.CASCADE,
        verbose_name="المستخدم", related_name="core_profile"
    )
    role = models.CharField(max_length=10, choices=USER_ROLES, default='STUDENT', verbose_name="الدور")
    pin_code = models.CharField(max_length=6, blank=True, verbose_name="رمز التحقق (PIN)")
    # ✅ حقل رقم الهوية الجديد
    national_id = models.CharField(max_length=10, blank=True, default="", verbose_name="رقم الهوية")

    class Meta:
        verbose_name = "4. ملفات المستخدمين"
        verbose_name_plural = "4. ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"