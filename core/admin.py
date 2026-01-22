from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# --- تنظيف العناوين الرئيسية في لوحة الإدارة ---
admin.site.site_header = "إدارة منصة آمنة التعليمية"
admin.site.index_title = "لوحة التحكم بالعناصر"

# --- 1. نظام الأسئلة المدمج (الإصدار المنظم) ---
# تم تغيير النوع إلى StackedInline ليأخذ كل سؤال وخيار عرض الصفحة كاملاً
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1  
    
    # تنظيم الحقول داخل الأسئلة لتكون مريحة للمعلمة
    fieldsets = (
        (None, {
            'fields': ('test_type', 'question_text'),
        }),
        ('خيارات الإجابة', {
            'fields': (
                ('option_a', 'option_b'), # وضعنا أ و ب بجانب بعض للتوفير لكن بمساحة واسعة
                ('option_c', 'option_d'), # ج و د بجانب بعض
            ),
        }),
        ('النتيجة والتغذية الراجعة', {
            'fields': ('correct_answer', 'feedback'),
        }),
    )
    
    verbose_name = "سؤال الاختبار"
    verbose_name_plural = "بنك أسئلة المهارة (قبلي وبعدي)"

@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ("platform_name", "principal_name", "updated_at")

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "user") 
    search_fields = ("name",)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    # --- عرض البيانات في القائمة ---
    list_display = ("title", "category", "get_teachers", "required_questions_count")
    list_filter = ("category",)
    filter_horizontal = ("teachers",) 
    
    # --- إضافة الأسئلة داخل الصفحة ---
    inlines = [QuestionInline]

    # --- تنسيق الحقول بشكل احترافي للمعلمة ---
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'category', 'teachers', 'required_questions_count')
        }),
        ('محتوى الشرح (مرونة المعلمة)', {
            'fields': ('content_text', 'video_url', 'pdf_file', 'image_explainer'),
            'description': 'يمكن للمعلمة وضع الشرح بصيغة نص أو رموز رياضية، فيديو، PDF، أو صورة.'
        }),
        ('تنسيق البطاقة (الإعدادات البصرية)', {
            'fields': ('icon_image', 'short_description', 'card_color'),
            'classes': ('collapse',), 
        }),
    )

    def get_teachers(self, obj):
        return ", ".join([t.name for t in obj.teachers.all()])
    get_teachers.short_description = "المعلمات المسؤولات"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "skill", "test_type", "correct_answer")
    list_filter = ("test_type", "skill")
    search_fields = ("question_text",)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "pin_code")
    list_filter = ("role",)
