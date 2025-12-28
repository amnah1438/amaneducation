from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    """
    بيانات المعلمة (مرتبطة بحساب مستخدم).
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher",
        verbose_name="حساب المستخدم"
    )

    full_name = models.CharField(
        max_length=200,
        verbose_name="اسم المعلمة"
    )

    class Meta:
        verbose_name = "معلمة"
        verbose_name_plural = "المعلمات"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name
