from django.db import models
from django.contrib.auth.models import User
from core.models import Profile
from ckeditor_uploader.fields import RichTextUploadingField


class Teacher(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name="teacher", verbose_name="حساب المستخدم"
    )
    full_name = models.CharField(max_length=200, verbose_name="اسم المعلمة")

    class Meta:
        verbose_name = "معلمة"
        verbose_name_plural = "المعلمات"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


# ═══════════════════════════════════════
# المهارة (قدرات) والدرس (تحصيلي)
# ═══════════════════════════════════════

class Skill(models.Model):
    """مهارة قدرات — فيها قبلي + شرح + بعدي"""

    TYPE_CHOICES = [
        ('qodrat_kamy', 'قدرات — كمي'),
        ('qodrat_lafzy', 'قدرات — لفظي'),
    ]

    SUBJECT_CHOICES = [
        ('math', 'تحصيلي — رياضيات'),
        ('bio', 'تحصيلي — أحياء'),
        ('chem', 'تحصيلي — كيمياء'),
        ('phys', 'تحصيلي — فيزياء'),
    ]

    CONTENT_TYPE = [
        ('skill', 'مهارة قدرات'),
        ('lesson', 'درس تحصيلي'),
        ('bank', 'بنك أسئلة'),
    ]

    # المعلومات الأساسية
    content_type = models.CharField(
        max_length=10, choices=CONTENT_TYPE, default='skill',
        verbose_name="نوع المحتوى"
    )
    title = models.CharField(max_length=200, verbose_name="العنوان")
    skill_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES,
        blank=True, verbose_name="نوع القدرات"
    )
    subject = models.CharField(
        max_length=10, choices=SUBJECT_CHOICES,
        blank=True, verbose_name="مادة التحصيلي"
    )
    description = models.TextField(blank=True, verbose_name="وصف مختصر")

    # المعلمة المنشئة
    created_by = models.ForeignKey(
        Teacher, on_delete=models.CASCADE,
        related_name="skills", verbose_name="المعلمة المنشئة"
    )

    # الفصول المستهدفة
    target_classes = models.CharField(
        max_length=100, blank=True,
        verbose_name="الفصول المستهدفة",
        help_text="مثال: ث١٢,ث١١"
    )

    # المشاركة مع المعلمات
    is_shared = models.BooleanField(
        default=True, verbose_name="مشاركة مع المعلمات"
    )

    # الحالة
    is_active = models.BooleanField(default=False, verbose_name="مفعّلة")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مهارة / درس"
        verbose_name_plural = "المهارات والدروس"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_content_type_display()} — {self.title}"


# ═══════════════════════════════════════
# محتوى الشرح
# ═══════════════════════════════════════

class SkillContent(models.Model):
    """محتوى شرح المهارة أو الدرس"""

    skill = models.OneToOneField(
        Skill, on_delete=models.CASCADE,
        related_name="content", verbose_name="المهارة/الدرس"
    )

    # للكمي والرياضيات والفيزياء والكيمياء والأحياء — محرر علمي كامل
    text_content = RichTextUploadingField(
        config_name='scientific_editor',
        blank=True, null=True,
        verbose_name="شرح نصي (مع رموز ومعادلات)"
    )

    # للفظي — نص عادي وصورة فقط
    plain_text = models.TextField(
        blank=True, verbose_name="شرح نصي بسيط (للفظي)"
    )
    plain_image = models.ImageField(
        upload_to='skill_content/', blank=True, null=True,
        verbose_name="صورة توضيحية (للفظي)"
    )

    # مشترك
    video_url = models.URLField(blank=True, verbose_name="رابط فيديو")
    pdf_file = models.FileField(
        upload_to='skill_pdfs/', blank=True, null=True,
        verbose_name="ملف PDF"
    )

    class Meta:
        verbose_name = "محتوى الشرح"

    def __str__(self):
        return f"شرح — {self.skill.title}"


# ═══════════════════════════════════════
# الاختبار (قبلي / بعدي / تحصيلي / بنك)
# ═══════════════════════════════════════

class Exam(models.Model):
    """اختبار مرتبط بمهارة أو درس"""

    EXAM_TYPE = [
        ('pre', 'اختبار قبلي'),
        ('post', 'اختبار بعدي'),
        ('lesson', 'اختبار درس تحصيلي'),
        ('bank', 'اختبار من بنك الأسئلة'),
    ]

    DELIVERY_TYPE = [
        ('electronic', 'إلكتروني فقط'),
        ('paper', 'ورقي فقط'),
        ('both', 'إلكتروني + ورقي'),
    ]

    CORRECTION_TYPE = [
        ('auto', 'تلقائي'),
        ('manual', 'يدوي'),
        ('both', 'كلاهما'),
    ]

    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE,
        related_name="exams", verbose_name="المهارة/الدرس"
    )
    exam_type = models.CharField(
        max_length=10, choices=EXAM_TYPE, verbose_name="نوع الاختبار"
    )

    # إعدادات الاختبار
    questions_count = models.PositiveIntegerField(
        default=10, verbose_name="عدد الأسئلة"
    )
    duration_minutes = models.PositiveIntegerField(
        default=15, verbose_name="مدة الاختبار (دقيقة)"
    )
    pass_score = models.PositiveIntegerField(
        default=60, verbose_name="درجة النجاح %"
    )

    # التواريخ
    start_date = models.DateField(
        blank=True, null=True, verbose_name="تاريخ البدء"
    )
    end_date = models.DateField(
        blank=True, null=True, verbose_name="تاريخ الانتهاء"
    )

    # طريقة التسليم والتصحيح
    delivery = models.CharField(
        max_length=15, choices=DELIVERY_TYPE,
        default='both', verbose_name="طريقة التسليم"
    )
    correction = models.CharField(
        max_length=10, choices=CORRECTION_TYPE,
        default='auto', verbose_name="طريقة التصحيح"
    )

    is_active = models.BooleanField(default=False, verbose_name="مفعّل")
    shuffle_questions = models.BooleanField(
        default=True, verbose_name="ترتيب عشوائي للأسئلة"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "اختبار"
        verbose_name_plural = "الاختبارات"

    def __str__(self):
        return f"{self.get_exam_type_display()} — {self.skill.title}"


# ═══════════════════════════════════════
# الأسئلة
# ═══════════════════════════════════════

class Question(models.Model):
    """سؤال في اختبار أو بنك أسئلة"""

    CORRECT_CHOICES = [
        ('A', 'أ'), ('B', 'ب'), ('C', 'ج'), ('D', 'د'),
    ]

    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE,
        related_name="questions", verbose_name="الاختبار"
    )

    # المهارة المستهدفة من هذا السؤال (للبنك)
    target_skill_name = models.CharField(
        max_length=200, blank=True,
        verbose_name="المهارة المستهدفة",
        help_text="للبنك فقط — اسم المهارة أو الدرس"
    )

    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")

    # نص السؤال
    # للكمي والتحصيلي — محرر علمي كامل
    question_text = RichTextUploadingField(
        config_name='scientific_editor',
        blank=True, null=True,
        verbose_name="نص السؤال (مع رموز)"
    )

    # للفظي — نص عادي وصورة
    question_plain = models.TextField(
        blank=True, verbose_name="نص السؤال البسيط (للفظي)"
    )
    question_image = models.ImageField(
        upload_to='questions/', blank=True, null=True,
        verbose_name="صورة السؤال"
    )

    # الخيارات — محرر علمي للكمي والتحصيلي
    option_a = RichTextUploadingField(
        config_name='scientific_editor',
        blank=True, null=True, verbose_name="خيار أ"
    )
    option_b = RichTextUploadingField(
        config_name='scientific_editor',
        blank=True, null=True, verbose_name="خيار ب"
    )
    option_c = RichTextUploadingField(
        config_name='scientific_editor',
        blank=True, null=True, verbose_name="خيار ج"
    )
    option_d = RichTextUploadingField(
        config_name='scientific_editor',
        blank=True, null=True, verbose_name="خيار د"
    )

    # خيارات نصية بسيطة للفظي
    option_a_plain = models.CharField(max_length=500, blank=True, verbose_name="خيار أ (نص)")
    option_b_plain = models.CharField(max_length=500, blank=True, verbose_name="خيار ب (نص)")
    option_c_plain = models.CharField(max_length=500, blank=True, verbose_name="خيار ج (نص)")
    option_d_plain = models.CharField(max_length=500, blank=True, verbose_name="خيار د (نص)")

    correct_answer = models.CharField(
        max_length=1, choices=CORRECT_CHOICES,
        verbose_name="الإجابة الصحيحة"
    )

    # تغذية راجعة
    feedback = RichTextUploadingField(
        config_name='scientific_editor',
        blank=True, null=True,
        verbose_name="تغذية راجعة"
    )
    feedback_plain = models.TextField(
        blank=True, verbose_name="تغذية راجعة بسيطة (للفظي)"
    )

    class Meta:
        verbose_name = "سؤال"
        verbose_name_plural = "الأسئلة"
        ordering = ["order"]

    def __str__(self):
        from django.utils.html import strip_tags
        text = strip_tags(self.question_text or self.question_plain or "")
        return f"س{self.order} — {text[:50]}"


# ═══════════════════════════════════════
# نتائج الطالبات
# ═══════════════════════════════════════

class ExamResult(models.Model):
    """نتيجة اختبار طالبة"""

    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE,
        related_name="results", verbose_name="الاختبار"
    )
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="exam_results", verbose_name="الطالبة"
    )

    score = models.FloatField(default=0, verbose_name="الدرجة")
    total = models.PositiveIntegerField(default=10, verbose_name="الدرجة الكاملة")
    percentage = models.FloatField(default=0, verbose_name="النسبة المئوية %")
    passed = models.BooleanField(default=False, verbose_name="ناجحة")

    # وقت الاختبار
    time_taken_seconds = models.PositiveIntegerField(
        default=0, verbose_name="الوقت المستغرق (ثانية)"
    )

    # التصحيح اليدوي
    manually_corrected = models.BooleanField(
        default=False, verbose_name="صُحّح يدوياً"
    )
    corrected_by = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="corrected_results",
        verbose_name="صحّحتها"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نتيجة اختبار"
        verbose_name_plural = "نتائج الاختبارات"
        unique_together = ['exam', 'student']

    def __str__(self):
        return f"{self.student.username} — {self.exam} — {self.score}/{self.total}"


class StudentAnswer(models.Model):
    """إجابة طالبة على سؤال معين"""

    result = models.ForeignKey(
        ExamResult, on_delete=models.CASCADE,
        related_name="answers", verbose_name="النتيجة"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE,
        verbose_name="السؤال"
    )
    chosen_answer = models.CharField(
        max_length=1, verbose_name="الإجابة المختارة"
    )
    is_correct = models.BooleanField(default=False, verbose_name="صحيحة")

    class Meta:
        verbose_name = "إجابة طالبة"
        verbose_name_plural = "إجابات الطالبات"

    def __str__(self):
        return f"{self.result.student.username} — س{self.question.order} — {'✓' if self.is_correct else '✗'}"


# ═══════════════════════════════════════
# سجل الحصص
# ═══════════════════════════════════════

class ClassSession(models.Model):
    """سجل حصة مفعّلة"""

    SESSION_TYPE = [
        ('qodrat', 'قدرات'),
        ('tahsili', 'تحصيلي'),
        ('both', 'قدرات + تحصيلي'),
    ]

    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE,
        related_name="sessions", verbose_name="المعلمة"
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE,
        related_name="sessions", verbose_name="المهارة/الدرس"
    )
    exam = models.ForeignKey(
        Exam, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="sessions", verbose_name="الاختبار المفعّل"
    )

    session_type = models.CharField(
        max_length=10, choices=SESSION_TYPE,
        default='qodrat', verbose_name="نوع الحصة"
    )
    target_class = models.CharField(
        max_length=50, verbose_name="الفصل المستهدف"
    )
    session_date = models.DateField(verbose_name="تاريخ الحصة")
    session_time = models.TimeField(verbose_name="وقت الحصة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سجل حصة"
        verbose_name_plural = "سجل الحصص"
        ordering = ["-session_date", "-session_time"]

    def __str__(self):
        return f"{self.teacher.full_name} — {self.skill.title} — {self.session_date}"