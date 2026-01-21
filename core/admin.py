from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# --- تنظيف العناوين الرئيسية في لوحة الإدارة (لمساتكِ الأصلية) ---
admin.site.site_header = "إدارة منصة آمنة التعليمية"
admin.site.index_title = "لوحة التحكم بالعناصر"

# --- 1. نظام الأسئلة المدمج (Inline) ---
# هذا الجزء يسمح للمعلمة بإضافة الأسئلة داخل صفحة المهارة مباشرة
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # عدد الصفوف الفارغة للإضافة السريعة
    fields = ('test_type', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'feedback')
    verbose_name = "سؤال الاختبار"
    verbose_name_plural = "بنك أسئلة المهارة (قبلي وبعدي)"

@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ("platform_name", "principal_name", "updated_at")

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "user") # أضفنا اليوزر للتأكد من ربط الحساب
    search_fields = ("name",)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    # --- عرض البيانات في القائمة (شغلك السابق) ---
    list_display = ("title", "category", "get_teachers", "required_questions_count")
    list_filter = ("category",)
    filter_horizontal = ("teachers",) # الصناديق التي أعجبتك لاختيار المعلمات
    
    # --- إضافة الأسئلة داخل الصفحة ---
    inlines = [QuestionInline]

    # --- تنسيق الحقول بشكل احترافي للمعلمة ---
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'category', 'teachers', 'required_questions_count')
        }),
        ('محتوى الشرح (مرونة المعلمة)', {
            'fields': ('content_text', 'video_url', 'pdf_file', 'image_explainer'),
            'description': 'يمكن للمعلمة وضع الشرح بصيغة نص، فيديو، PDF، أو صورة.'
        }),
        ('تنسيق البطاقة (شغلك السابق)', {
            'fields': ('icon_image', 'short_description', 'card_color'),
            'classes': ('collapse',), # القسم يكون مغلقاً ويفتح عند الحاجة
        }),
    )

    def get_teachers(self, obj):
        return ", ".join([t.name for t in obj.teachers.all()])
    get_teachers.short_description = "المعلمات المسؤولات"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """ لعرض الأسئلة بشكل منفصل إذا رغبتِ في البحث عنها """
    list_display = ("question_text", "skill", "test_type", "correct_answer")
    list_filter = ("test_type", "skill")
    search_fields = ("question_text",)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "pin_code")
    list_filter = ("role",)
