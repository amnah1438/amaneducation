from django.contrib import admin
from .models import (
    Teacher, TeacherSkill, TeacherSkillContent,
    TeacherExam, TeacherQuestion, ExamResult,
    StudentAnswer, ClassSession
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user")
    search_fields = ("full_name", "user__username")


@admin.register(TeacherSkill)
class TeacherSkillAdmin(admin.ModelAdmin):
    list_display = ("title", "content_type", "skill_type", "subject", "created_by", "target_classes", "is_active", "is_shared", "created_at")
    list_filter = ("content_type", "skill_type", "subject", "is_active", "is_shared")
    search_fields = ("title", "description")
    list_editable = ("is_active", "is_shared")
    ordering = ("-created_at",)


@admin.register(TeacherSkillContent)
class TeacherSkillContentAdmin(admin.ModelAdmin):
    list_display = ("skill", "video_url")
    search_fields = ("skill__title",)


@admin.register(TeacherExam)
class TeacherExamAdmin(admin.ModelAdmin):
    list_display = ("skill", "exam_type", "questions_count", "duration_minutes", "pass_score", "delivery", "correction", "is_active", "start_date", "end_date")
    list_filter = ("exam_type", "delivery", "correction", "is_active")
    list_editable = ("is_active",)
    ordering = ("-created_at",)


@admin.register(TeacherQuestion)
class TeacherQuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "order", "correct_answer", "target_skill_name")
    list_filter = ("correct_answer", "exam__exam_type")
    search_fields = ("question_plain", "target_skill_name")
    ordering = ("exam", "order")


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "score", "total", "percentage", "passed", "manually_corrected", "submitted_at")
    list_filter = ("passed", "manually_corrected")
    search_fields = ("student__username",)
    ordering = ("-submitted_at",)


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ("result", "question", "chosen_answer", "is_correct")
    list_filter = ("is_correct",)


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ("teacher", "skill", "session_type", "target_class", "session_date", "session_time")
    list_filter = ("session_type", "target_class")
    search_fields = ("teacher__full_name", "skill__title")
    ordering = ("-session_date", "-session_time")