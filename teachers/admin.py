from django.contrib import admin
from .models import ExamResult, ClassSession


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'total', 'percentage', 'passed', 'submitted_at')
    list_filter = ('passed', 'submitted_at')
    search_fields = ('student__username', 'student__first_name')
    ordering = ('-submitted_at',)
    readonly_fields = ('student', 'exam', 'score', 'total', 'percentage', 'passed', 'submitted_at')
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'skill', 'session_type', 'target_class', 'session_date')
    list_filter = ('session_type', 'session_date')
    ordering = ('-session_date',)
    readonly_fields = ('teacher', 'skill', 'session_type', 'target_class', 'session_date', 'session_time')
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False