from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin", "إدارة"
    TEACHER = "teacher", "معلمة"
    STUDENT = "student", "طالبة"