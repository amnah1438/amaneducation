from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill

# 1. إعدادات الهوية الرسمية (شغلك الأخير)
@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "platform_name",
        "principal_name",
        "updated_at",
    )

# 2. إدارة ملفات المستخدمين (Profile)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "pin_code")
    list_filter = ("role",)

# 3. إدارة أسماء المعلمات (لكي تضيفيهن أولاً)
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

# 4. إدارة المهارات والدروس (التي تسمح باختيار معلمات متعددات)
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "display_teachers")
    list_filter = ("category",)
    search_fields = ("title",)
    # هذا السطر يجعل اختيار المعلمات سهلاً جداً (صندوقين للمبادلة)
    filter_horizontal = ("teachers",) 

    def display_teachers(self, obj):
        return ", ".join([teacher.name for teacher in obj.teachers.all()])
    display_teachers.short_description = "المعلمات المسؤولات"