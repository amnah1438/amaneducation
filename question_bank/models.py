from django.db import models
from skills.models import Skill


class Difficulty(models.IntegerChoices):
    EASY = 1, "سهل"
    MEDIUM = 2, "متوسط"
    HARD = 3, "صعب"


class Question(models.Model):
    """
    سؤال ضمن بنك أسئلة مهارة.
    يدعم LaTeX داخل نص السؤال والتفسير.
    """

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="المهارة"
    )

    text = models.TextField(
        verbose_name="نص السؤال (يدعم LaTeX)"
    )

    option_a = models.CharField(
        max_length=300,
        verbose_name="الخيار A"
    )

    option_b = models.CharField(
        max_length=300,
        verbose_name="الخيار B"
    )

    option_c = models.CharField(
        max_length=300,
        verbose_name="الخيار C"
    )

    option_d = models.CharField(
        max_length=300,
        verbose_name="الخيار D"
    )

    correct_option = models.CharField(
        max_length=1,
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
        verbose_name="الإجابة الصحيحة"
    )

    explanation = models.TextField(
        blank=True,
        default="",
        verbose_name="الشرح / التفسير (اختياري)"
    )

    difficulty = models.IntegerField(
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM,
        verbose_name="مستوى الصعوبة"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="السؤال مفعل"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإضافة"
    )

    class Meta:
        verbose_name = "سؤال"
        verbose_name_plural = "الأسئلة"
        ordering = ["-created_at"]

    def __str__(self):
        return f"سؤال: {self.skill.title}"
