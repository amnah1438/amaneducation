from django.contrib import admin
from .models import (
    Teacher, TeacherSkill, TeacherExam,
    TeacherQuestion, ExamResult, ClassSession
)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user')
    search_fields = ('full_name',)


@admin.register(TeacherSkill)
class TeacherSkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'created_by', 'target_classes', 'is_active', 'is_shared')
    list_filter = ('content_type', 'is_active', 'is_shared')
    search_fields = ('title',)
    list_editable = ('is_active', 'is_shared')
    ordering = ('-created_at',)


@admin.register(TeacherExam)
class TeacherExamAdmin(admin.ModelAdmin):
    list_display = ('skill', 'exam_type', 'questions_count', 'duration_minutes', 'is_active')
    list_filter = ('exam_type', 'is_active')
    list_editable = ('is_active',)


@admin.register(TeacherQuestion)
class TeacherQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'order', 'correct_answer')
    list_filter = ('exam__exam_type',)
    search_fields = ('question_plain',)
    ordering = ('exam', 'order')


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'total', 'percentage', 'passed', 'submitted_at')
    list_filter = ('passed',)
    search_fields = ('student__username',)
    ordering = ('-submitted_at',)


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'skill', 'session_type', 'target_class', 'session_date')
    list_filter = ('session_type',)
    ordering = ('-session_date',)