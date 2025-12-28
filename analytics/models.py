from django.db import models


class DailyStat(models.Model):
    """
    إحصاءات يومية مبسطة (اختياري للتوسع).
    """
    date = models.DateField(unique=True)
    attempts_count = models.PositiveIntegerField(default=0)
    avg_score = models.FloatField(default=0)

    def __str__(self):
        return str(self.date)
