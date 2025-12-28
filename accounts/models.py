from django.db import models
from django.contrib.auth.models import User


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    TEACHER = "teacher", "Teacher"


class Profile(models.Model):
    """
    ملف المستخدم: يحدد هل هو معلمة أو إدارة.
    نستخدم User الافتراضي من Django لسهولة الدخول والأمان.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.TEACHER)
    pin_code = models.CharField(max_length=10, blank=True, default="")

    def __str__(self):
        return f"{self.user.username} ({self.role})"
