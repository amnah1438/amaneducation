from django.db import models
from skills.models import Skill


class Difficulty(models.IntegerChoices):
    EASY = 1, "سهل"
    MEDIUM = 2, "متوسط"
    HARD = 3, "صعب"


class Question(models.Model):
    """
    سؤال ضمن بنك أسئلة مهارة.
    يدعم LaTeX داخل text/explanation.
    """
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)

    correct_option = models.CharField(max_length=1, choices=[("A","A"),("B","B"),("C","C"),("D","D")])
    explanation = models.TextField(blank=True, default="")

    difficulty = models.IntegerField(choices=Difficulty.choices, default=Difficulty.MEDIUM)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q({self.skill.title})"
