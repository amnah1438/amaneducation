from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# 1. تخصيص عنوان لوحة التحكم
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"
admin.site.site_title = "لوحة تحكم آمنة"
admin.site.index_title = "مرحباً بكِ في إدارة المحتوى"

# 2. إعداد الأسئلة (Inline) لتظهر تحت المهارة بشكل مرتب
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

# 3. تسجيل المهارات (Skill) مع تنسيق الألوان وحذف الأدوات
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]
    
    # تنظيم الحقول الموجودة فعلياً في كودك (تم حذف الحقول المسببة للخطأ)
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'category', 'short_description')
        }),
        ('المحتوى التعليمي (فيديو وملفات)', {
            'fields': ('video_url', 'content_text', 'image_explainer', 'pdf_file'),
            'description': '💡 روابط اليوتيوب والدرايف ستعمل تلقائياً عند وضعها هنا.'
        }),
        ('إعدادات إضافية', {
            'fields': ('card_color',), 
        }),
    )

    def render_change_form(self, request, context, **kwargs):
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        
        # كود التنسيق البنفسجي وتنظيف المحرر (بدون بوكس الأدوات)
        custom_admin_js_css = """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                if (typeof CKEDITOR !== 'undefined') {
                    CKEDITOR.on('instanceReady', function(ev) {
                        ev.editor.config.contentsLangDirection = 'rtl';
                        ev.editor.config.entities = false; 
                        ev.editor.config.basicEntities = false;
                        ev.editor.editable().setStyle('font-family', 'Cairo, sans-serif');
                    });
                }
            });
        </script>
        <style>
            /* تنسيق الألوان البنفسجية الملكية */
            :root { --primary: #6f42c1; }
            #header { background: #6f42c1 !important; color: white !important; }
            .module h2, .module caption, .inline-group h2 { background: #59359a !important; color: white !important; }
            div.breadcrumbs { background: #f3f0f7 !important; color: #6f42c1 !important; border-bottom: 1px solid #e0d9f0; }
            div.breadcrumbs a { color: #6f42c1 !important; }
            .button, input[type=submit], input[type=button], .submit-row input { 
                background: #6f42c1 !important; 
                border-radius: 8px !important; 
                padding: 10px 20px !important;
                font-weight: bold !important;
            }
            .button:hover, input[type=submit]:hover { background: #59359a !important; }
            /* تحسين شكل البوكسات */
            .inline-related { border: 1px solid #e0d9f0 !important; border-radius: 10px !important; overflow: hidden; margin-bottom: 20px !important; }
        </style>
        """
        content = response.content.decode('utf-8')
        new_content = content.replace('</body>', custom_admin_js_css + '</body>')
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
