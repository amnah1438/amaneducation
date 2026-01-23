from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# 1. تخصيص عنوان وألوان لوحة التحكم (التنسيق الجمالي)
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"
admin.site.site_title = "لوحة تحكم آمنة"
admin.site.index_title = "مرحباً بكِ في إدارة المحتوى"

# إضافة لمسة جمالية ملونة للأدمن (Purple Theme)
class MyAdminConfig:
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',)
        }

# 2. إعداد الأسئلة (Inline) لتظهر تحت المهارة بشكل مرتب
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    # تم الإبقاء على الحقول تلقائية كما طلبتِ

# 3. تسجيل المهارات (Skill) بتنسيق الحقول المرتب
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]
    
    # تنظيم الحقول في مجموعات ملونة ومرتبة
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'category', 'short_description')
        }),
        ('المحتوى التعليمي (فيديو وملفات)', {
            'fields': ('video_url', 'content_text', 'image_explainer', 'pdf_file'),
            'description': '💡 نصيحة: روابط اليوتيوب والدرايف سيتم تصحيحها تلقائياً لتفتح في المنصة.'
        }),
        ('تصميم البطاقة', {
            'fields': ('card_color', 'skill_icon', 'test_questions_count'),
        }),
    )

    # كود JS بسيط لتنظيف المحرر ومنع الرموز الغريبة فقط (بدون بوكس الأدوات)
    def render_change_form(self, request, context, **kwargs):
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        
        clean_js = """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                if (typeof CKEDITOR !== 'undefined') {
                    CKEDITOR.on('instanceReady', function(ev) {
                        ev.editor.config.contentsLangDirection = 'rtl';
                        ev.editor.config.entities = false; 
                        ev.editor.config.basicEntities = false;
                    });
                }
            });
        </script>
        <style>
            /* تلوين واجهة الأدمن باللون البنفسجي */
            :root { --primary: #6f42c1; --secondary: #59359a; }
            #header { background: #6f42c1 !important; }
            .module h2, .module caption, .inline-group h2 { background: #59359a !important; }
            div.breadcrumbs { background: #f3f0f7 !important; color: #6f42c1 !important; }
            .button, input[type=submit], input[type=button], .submit-row input { background: #6f42c1 !important; }
        </style>
        """
        content = response.content.decode('utf-8')
        new_content = content.replace('</body>', clean_js + '</body>')
        response.content = new_content.encode('utf-8')
        return response

# 4. تسجيل الأسئلة بشكل منفصل
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')
    search_fields = ('question_text',)

# 5. تسجيل باقي الأقسام
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
