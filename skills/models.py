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
    مهارة (تأسيس ضمن القدرات: لفظي/كمي) أو مهارة/موضوع ضمن التحصيلي حسب القسم.
    """
    track = models.CharField(max_length=20, choices=Track.choices, default=Track.QUDURAT)
    section = models.CharField(max_length=20, choices=Section.choices)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, default="")

    teacher_owner = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="skills")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["track", "section", "title"]

    def __str__(self):
        return self.title
