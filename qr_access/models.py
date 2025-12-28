from django.db import models
from teachers.models import Teacher
from students.models import ClassRoom
from skills.models import Skill


class QRSession(models.Model):
    """
    جلسة دخول للحصة عبر QR / رابط.
    تُستخدم لربط الحصة بفصل ومهارة ومعلمة.
    """
    token = models.CharField(max_length=64, unique=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="qr_sessions")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="qr_sessions")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="qr_sessions")

    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
