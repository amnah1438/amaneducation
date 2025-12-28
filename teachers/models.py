from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    """
    بيانات المعلمة (مرتبطة بحساب User).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher")
    full_name = models.CharField(max_length=200)

    def __str__(self):
        return self.full_name
