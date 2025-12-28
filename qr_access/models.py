from django.db import models
from teachers.models import Teacher
from students.models import ClassRoom
from skills.models import Skill


class QRSession(models.Model):
    """
    جلسة دخول للحصة عبر QR / رابط.
    تُستخدم لربط الحصة بفصل ومهارة ومعلمة.
    """

    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="رمز الجلسة"
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="qr_sessions",
        verbose_name="المعلمة"
    )

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name="qr_sessions",
        verbose_name="الفصل"
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="qr_sessions",
        verbose_name="المهارة"
    )

    expires_at = models.DateTimeField(
        verbose_name="تاريخ ووقت الانتهاء"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="الجلسة مفعّلة"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "جلسة دخول عبر QR"
        verbose_name_plural = "جلسات الدخول عبر QR"
        ordering = ["-created_at"]

    def __str__(self):
        return f"جلسة {self.classroom} – {self.skill}"
