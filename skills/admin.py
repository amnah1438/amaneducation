from django.contrib import admin
from .models import Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "track",
        "section",
        "teacher_owner",
        "is_active",
    )
    list_filter = ("track", "section", "is_active")
    search_fields = ("title",)
