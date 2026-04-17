from django.contrib import admin
from .models import SchoolSettings, Profile, Skill, Question

admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"
admin.site.site_title = "منصة آمنة"
admin.site.index_title = "لوحة التحكم"


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ('platform_name', 'principal_name', 'updated_at')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'national_id')
    list_filter = ('role',)
    search_fields = ('user__username', 'national_id')


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('skill',)
    list_filter = ('skill',)