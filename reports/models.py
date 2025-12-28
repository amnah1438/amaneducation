from django.db import models
from assessments.models import Attempt


class ReportFile(models.Model):
    """
    ملف تقرير صادر (PDF/صورة) مرتبط بمحاولة.
    """
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="report_files")

    file_pdf = models.FileField(upload_to="reports/", blank=True, null=True)
    file_image = models.ImageField(upload_to="reports/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.attempt}"
