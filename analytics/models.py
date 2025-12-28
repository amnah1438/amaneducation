from django.db import models


class DailyStat(models.Model):
    """
    إحصاءات يومية مبسطة تُستخدم للتحليل العام للأداء.
    """

    date = models.DateField(
        unique=True,
        verbose_name="التاريخ"
    )

    attempts_count = models.PositiveIntegerField(
        default=0,
        verbose_name="عدد المحاولات"
    )

    avg_score = models.FloatField(
        default=0,
        verbose_name="متوسط الدرجة"
    )

    class Meta:
        verbose_name = "إحصائية يومية"
        verbose_name_plural = "الإحصاءات اليومية"
        ordering = ["-date"]

    def __str__(self):
        return f"إحصائيات {self.date}"
