from django.db import models
from teachers.models import Teacher
from students.models import ClassRoom, Student
from skills.models import Skill
from question_bank.models import Question


class AssessmentType(models.TextChoices):
    PRE = "pre", "اختبار قبلي"
    POST = "post", "اختبار بعدي"
    PRACTICE = "practice", "تدريب"


class Assessment(models.Model):
    """
    اختبار/تدريب مرتبط بمهارة + فصل + معلمة.
    """
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="assessments",
        verbose_name="المهارة"
    )

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="assessments",
        verbose_name="الفصل"
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="assessments",
        verbose_name="المعلمة"
    )

    title = models.CharField(
        max_length=250,
        verbose_name="عنوان الاختبار/التدريب"
    )

    assessment_type = models.CharField(
        max_length=20,
        choices=AssessmentType.choices,
        verbose_name="نوع التقييم"
    )

    duration_minutes = models.PositiveIntegerField(
        default=10,
        verbose_name="مدة الوقت (بالدقائق)"
    )

    is_open = models.BooleanField(
        default=False,
        verbose_name="مفتوح للطالبات؟"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    questions = models.ManyToManyField(
        Question,
        blank=True,
        related_name="assessments",
        verbose_name="الأسئلة"
    )

    class Meta:
        verbose_name = "اختبار/تدريب"
        verbose_name_plural = "الاختبارات والتدريبات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_assessment_type_display()})"
    

class Attempt(models.Model):
    """
    محاولة طالبة للاختبار/التدريب (تُستخدم للتقارير التفصيلية).
    """
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="الاختبار/التدريب"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="الطالبة"
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="وقت البدء"
    )

    submitted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="وقت التسليم"
    )

    score = models.FloatField(
        default=0,
        verbose_name="الدرجة"
    )

    total = models.PositiveIntegerField(
        default=0,
        verbose_name="الدرجة الكاملة"
    )

    class Meta:
        verbose_name = "محاولة"
        verbose_name_plural = "محاولات الطالبات"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student} - {self.assessment}"
    

class AttemptAnswer(models.Model):
    """
    إجابة سؤال داخل محاولة.
    """
    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="المحاولة"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="السؤال"
    )

    chosen_option = models.CharField(
        max_length=1,
        blank=True,
        default="",
        verbose_name="الإجابة المختارة"
    )

    is_correct = models.BooleanField(
        default=False,
        verbose_name="صحيحة؟"
    )

    class Meta:
        verbose_name = "إجابة داخل محاولة"
        verbose_name_plural = "إجابات المحاولات"

    def __str__(self):
        return f"{self.attempt} - سؤال"
