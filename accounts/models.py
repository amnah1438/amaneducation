from django.db import models
from django.contrib.auth.models import User


class UserRole(models.TextChoices):
    ADMIN = "admin", "إدارة"
    TEACHER = "teacher", "معلمة"
    STUDENT = "student", "طالبة"


class Profile(models.Model):
    """
    ملف المستخدم: يحدد هل هو معلمة أو إدارة أو طالبة.
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

    # حقول خاصة بالطالبة
    classroom = models.ForeignKey(
        'students.ClassRoom',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="profiles",
        verbose_name="الفصل"
    )

    # حقول خاصة بالمعلمة
    school_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="اسم المدرسة"
    )

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == UserRole.ADMIN

    def is_teacher(self):
        return self.role == UserRole.TEACHER

    def is_student(self):
        return self.role == UserRole.STUDENT