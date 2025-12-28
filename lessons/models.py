from django.db import models
from teachers.models import Teacher
from students.models import ClassRoom
from skills.models import Skill


class Lesson(models.Model):
    """
    درس مرتبط بمهارة + فصل + معلمة.
    """
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="lessons")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="lessons")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="lessons")

    title = models.CharField(max_length=250)
    content = models.TextField(blank=True, default="")  # نص + LaTeX داخل $$ $$ أو \( \)
    created_at = models.DateTimeField(auto_now_add=True)

    # إتاحة طباعة الدرس كـ PDF لاحقًا (مسار ملف التصدير)
    exported_pdf = models.FileField(upload_to="lessons/", blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.classroom}"
