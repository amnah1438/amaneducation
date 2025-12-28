from django.db import models
from teachers.models import Teacher
from students.models import ClassRoom, Student
from skills.models import Skill
from question_bank.models import Question


class AssessmentType(models.TextChoices):
    PRE = "pre", "اختبار قبلي"
    POST = "post", "اختبار بعدي"
    PRACTICE = "practice", "تدريب"


class Assessment(models.Model):
    """
    اختبار/تدريب مرتبط بمهارة + فصل + معلمة.
    """
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="assessments")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="assessments")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="assessments")

    title = models.CharField(max_length=250)
    assessment_type = models.CharField(max_length=20, choices=AssessmentType.choices)

    duration_minutes = models.PositiveIntegerField(default=10)  # مؤقت الاختبار
    is_open = models.BooleanField(default=False)  # المعلمة تفتح الاختبار
    created_at = models.DateTimeField(auto_now_add=True)

    questions = models.ManyToManyField(Question, blank=True, related_name="assessments")

    def __str__(self):
        return f"{self.title} ({self.assessment_type})"


class Attempt(models.Model):
    """
    محاولة طالبة للاختبار/التدريب (تُستخدم للتقارير التفصيلية).
    """
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attempts")

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)

    score = models.FloatField(default=0)
    total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.student} - {self.assessment}"


class AttemptAnswer(models.Model):
    """
    إجابة سؤال داخل محاولة.
    """
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    chosen_option = models.CharField(max_length=1, blank=True, default="")
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt} - Q"
