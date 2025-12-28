from django.db import models
from django.contrib.auth.models import User


class UserRole(models.TextChoices):
    ADMIN = "admin", "إدارة"
    TEACHER = "teacher", "معلمة"


class Profile(models.Model):
    """
    ملف المستخدم: يحدد هل هو معلمة أو إدارة.
    نستخدم User الافتراضي من Django لسهولة الدخول والأمان.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="المستخدم"
    )

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.TEACHER,
        verbose_name="الدور"
    )

    pin_code = models.CharField(
        max_length=10,
        blank=True,
        default="",
        verbose_name="رمز الـ PIN"
    )

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
