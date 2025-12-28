from django.contrib import admin
from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "skill", "classroom", "teacher", "created_at")
    list_filter = ("classroom", "teacher")
