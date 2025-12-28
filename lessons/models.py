from django.db import models
from teachers.models import Teacher
from students.models import ClassRoom
from skills.models import Skill


class Lesson(models.Model):
    """
    درس مرتبط بمهارة + فصل + معلمة.
    """

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="المهارة"
    )

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="الفصل"
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="المعلمة"
    )

    title = models.CharField(
        max_length=250,
        verbose_name="عنوان الدرس"
    )

    content = models.TextField(
        blank=True,
        default="",
        verbose_name="محتوى الدرس (يدعم LaTeX)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإضافة"
    )

    exported_pdf = models.FileField(
        upload_to="lessons/",
        blank=True,
        null=True,
        verbose_name="ملف الدرس (PDF)"
    )

    class Meta:
        verbose_name = "درس"
        verbose_name_plural = "الدروس"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.classroom}"
