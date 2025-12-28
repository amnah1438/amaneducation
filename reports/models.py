from django.db import models
from assessments.models import Attempt


class ReportFile(models.Model):
    """
    ملف تقرير صادر (PDF / صورة) مرتبط بمحاولة طالبة.
    """

    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name="report_files",
        verbose_name="المحاولة"
    )

    file_pdf = models.FileField(
        upload_to="reports/",
        blank=True,
        null=True,
        verbose_name="ملف التقرير (PDF)"
    )

    file_image = models.ImageField(
        upload_to="reports/",
        blank=True,
        null=True,
        verbose_name="صورة التقرير"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ إنشاء التقرير"
    )

    class Meta:
        verbose_name = "تقرير"
        verbose_name_plural = "التقارير"
        ordering = ["-created_at"]

    def __str__(self):
        return f"تقرير — {self.attempt}"
