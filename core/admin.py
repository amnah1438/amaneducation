from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# 1. تخصيص عنوان لوحة التحكم
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"
admin.site.site_title = "لوحة تحكم آمنة"
admin.site.index_title = "مرحباً بكِ في إدارة المحتوى"

# 2. إعداد الأسئلة (Inline) مع إضافة الفاصل البنفسجي العريض
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    # تحسين الواجهة بلمسة جمالية: فاصل بنفسجي واضح بين كل سؤال وسؤال
    classes = ['extra-spaced-inline'] 

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]
    
    fieldsets = (
        ('المعلومات الأساسية', {'fields': ('title', 'category', 'short_description')}),
        ('المحتوى التعليمي (فيديو وملفات)', {
            'fields': ('video_url', 'content_text', 'image_explainer', 'pdf_file'),
            'description': '💡 روابط اليوتيوب والدرايف ستعمل تلقائياً عند وضعها هنا.'
        }),
        ('إعدادات إضافية', {'fields': ('card_color',)}),
    )

    def render_change_form(self, request, context, **kwargs):
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        
        custom_admin_js_css = """
        <script>
            // وظيفة لإدراج "مربع نص حر" يمكن سحبه ووضعه في أي مكان (لحل مشكلة المسائل العمودية)
            function insertDraggableText(editorId) {
                var editor = CKEDITOR.instances[editorId];
                // المربع مصمم ليكون شفافاً بدون حدود عند العرض النهائي، وسهل التحريك أثناء الكتابة
                var html = '<div style="display:inline-block; border:1px dashed #6f42c1; padding:2px; cursor:move; position:relative; min-width:20px; text-align:center;">+</div>';
                editor.insertHtml(html);
            }

            document.addEventListener('DOMContentLoaded', function() {
                if (typeof CKEDITOR !== 'undefined') {
                    CKEDITOR.on('instanceReady', function(ev) {
                        ev.editor.config.contentsLangDirection = 'rtl';
                        // إضافة خيار التحكم في تباعد الأسطر (Line Height) في المحرر
                        ev.editor.config.line_height = "0.8;1.0;1.2;1.5;2.0";
                        ev.editor.editable().setStyle('font-family', 'Cairo, sans-serif');
                    });
                }
            });
        </script>
        <style>
            /* تنسيق الألوان البنفسجية الملكية */
            :root { --primary: #6f42c1; --light-purple: #f3f0f7; }
            #header { background: var(--primary) !important; }
            .module h2, .module caption, .inline-group h2 { background: #59359a !important; }
            
            /* --- اللمسة الجمالية: الفاصل البنفسجي بين الأسئلة --- */
            .inline-group .inline-related {
                border: 2px solid #e0d9f0 !important;
                border-top: 8px solid var(--primary) !important; /* فاصل علوي عريض بنفسجي */
                margin-bottom: 40px !important; /* مسافة كبيرة بين السؤال والآخر */
                box-shadow: 0 4px 6px rgba(111, 66, 193, 0.1);
            }
            .inline-group .inline-related h3 {
                background: var(--light-purple) !important;
                color: var(--primary) !important;
                border-bottom: 1px solid #e0d9f0;
            }
            
            /* زر إدراج النص الحر */
            .custom-tool-bar { margin: 10px 0; }
            .btn-free-text { 
                background: var(--light-purple); 
                border: 1px solid var(--primary); 
                color: var(--primary); 
                padding: 5px 12px; 
                border-radius: 5px; 
                cursor: pointer;
                font-size: 12px;
                font-weight: bold;
            }
            .btn-free-text:hover { background: var(--primary); color: white; }
        </style>
        """
        
        # إضافة الزر برمجياً فوق محررات النصوص
        tool_html = '<div class="custom-tool-bar"><button type="button" class="btn-free-text" onclick="insertDraggableText(this.parentElement.nextElementSibling.querySelector(\'textarea\').id)">➕ إدراج رمز حر (للتحريك)</button></div>'
        
        content = response.content.decode('utf-8')
        new_content = content.replace('</body>', custom_admin_js_css + '</body>')
        # وضع الزر قبل كل بلوك CKEditor
        new_content = new_content.replace('<div class="django-ckeditor-widget"', tool_html + '<div class="django-ckeditor-widget"')
        
        response.content = new_content.encode('utf-8')
        return response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')

admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
