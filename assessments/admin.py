from django.contrib import admin
from .models import Assessment, Attempt, AttemptAnswer


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "assessment_type",
        "skill",
        "classroom",
        "teacher",
        "is_open",
    )
    list_filter = ("assessment_type", "is_open")


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "assessment", "score", "total", "submitted_at")


@admin.register(AttemptAnswer)
class AttemptAnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "chosen_option", "is_correct")
