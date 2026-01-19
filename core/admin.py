from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill

# تنظيف العناوين الرئيسية في لوحة الإدارة
admin.site.site_header = "إدارة منصة آمنة التعليمية"
admin.site.index_title = "لوحة التحكم بالعناصر"

@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ("platform_name", "principal_name", "updated_at")

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    # عرض البيانات بشكل منظم في القائمة
    list_display = ("title", "category", "get_teachers")
    list_filter = ("category",)
    # تفعيل الصندوقين لاختيار أكثر من معلمة بسهولة
    filter_horizontal = ("teachers",) 

    def get_teachers(self, obj):
        return ", ".join([t.name for t in obj.teachers.all()])
    get_teachers.short_description = "المعلمات المسؤولات"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "pin_code")
    list_filter = ("role",)