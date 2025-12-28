from django.db import models
from teachers.models import Teacher


class Track(models.TextChoices):
    QUDURAT = "qudurat", "قدرات"
    TAHSILI = "tahsili", "تحصيلي"


class Section(models.TextChoices):
    # للقدرات
    VERBAL = "verbal", "لفظي"
    QUANT = "quant", "كمي"
    # للتحصيلي
    MATH = "math", "رياضيات"
    BIO = "bio", "أحياء"
    CHEM = "chem", "كيمياء"
    PHYS = "phys", "فيزياء"


class Skill(models.Model):
    """
    مهارة (تأسيس ضمن القدرات: لفظي/كمي)
    أو مهارة/موضوع ضمن التحصيلي حسب المادة.
    """

    track = models.CharField(
        max_length=20,
        choices=Track.choices,
        default=Track.QUDURAT,
        verbose_name="المسار"
    )

    section = models.CharField(
        max_length=20,
        choices=Section.choices,
        verbose_name="القسم / المادة"
    )

    title = models.CharField(
        max_length=250,
        verbose_name="اسم المهارة"
    )

    description = models.TextField(
        blank=True,
        default="",
        verbose_name="وصف المهارة"
    )

    teacher_owner = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="skills",
        verbose_name="المعلمة المسؤولة"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="مفعّلة"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإضافة"
    )

    class Meta:
        verbose_name = "مهارة"
        verbose_name_plural = "المهارات"
        ordering = ["track", "section", "title"]

    def __str__(self):
        return self.title
