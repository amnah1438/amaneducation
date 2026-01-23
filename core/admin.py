from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# 1. تخصيص عنوان لوحة التحكم
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"
admin.site.site_title = "لوحة تحكم آمنة"
admin.site.index_title = "مرحباً بكِ في إدارة المحتوى"

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]
    
    fieldsets = (
        ('المعلومات الأساسية', {'fields': ('title', 'category', 'short_description')}),
        ('المحتوى التعليمي (فيديو وملفات)', {'fields': ('video_url', 'content_text', 'image_explainer', 'pdf_file')}),
        ('إعدادات إضافية', {'fields': ('card_color',)}),
    )

    def render_change_form(self, request, context, **kwargs):
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        
        custom_logic = """
        <script>
            // وظيفة إدراج رمز "قابل للسحب" بمرونة تامة
            function insertMovableIcon(editorId) {
                var editor = CKEDITOR.instances[editorId];
                // كود HTML لرمز قابل للتحريك بالفأرة (Drag and Drop)
                var movableHtml = `
                    <span class="movable-symbol" contenteditable="true" 
                          style="display:inline-block; cursor:move; color:#6f42c1; font-weight:bold; padding:5px; border:1px dashed #ddd; position:relative;">
                        +
                    </span>`;
                editor.insertHtml(movableHtml);
            }

            document.addEventListener('DOMContentLoaded', function() {
                if (typeof CKEDITOR !== 'undefined') {
                    CKEDITOR.on('instanceReady', function(ev) {
                        ev.editor.config.contentsLangDirection = 'rtl';
                        // إضافة خيار تباعد الأسطر (Line Height)
                        ev.editor.config.extraPlugins = 'lineheight';
                        ev.editor.config.line_height = "0.5;0.8;1.0;1.2;1.5;2.0";
                        ev.editor.editable().setStyle('font-family', 'Cairo, sans-serif');
                    });
                }
            });
        </script>
        <style>
            /* تنسيق الألوان البنفسجية */
            :root { --primary: #6f42c1; --bg-light: #f8f6fc; }
            #header { background: var(--primary) !important; }
            .module h2 { background: #59359a !important; }
            
            /* --- اللمسة الجمالية: الفاصل البنفسجي العريض بين الأسئلة --- */
            .inline-group .inline-related {
                border: 3px solid #e0d9f0 !important;
                border-top: 12px solid var(--primary) !important; /* فاصل سميك جداً */
                margin-bottom: 50px !important;
                border-radius: 15px !important;
                box-shadow: 0 10px 20px rgba(111, 66, 193, 0.05);
            }

            /* زر التحريك الجديد */
            .custom-actions { margin-bottom: 10px; background: var(--bg-light); padding: 10px; border-radius: 8px; border: 1px solid #d1c4e9; }
            .drag-btn { background: white; border: 2px solid var(--primary); color: var(--primary); padding: 6px 15px; border-radius: 20px; cursor: pointer; font-weight: bold; transition: 0.3s; }
            .drag-btn:hover { background: var(--primary); color: white; }
            
            /* جعل الرموز قابلة للتحريك داخل المحرر */
            .movable-symbol:active { cursor: grabbing; outline: 2px solid var(--primary); }
        </style>
        """
        
        # حقن الأزرار فوق كل محرر سؤال
        tool_html = """
        <div class="custom-actions">
            <button type="button" class="drag-btn" onclick="insertMovableIcon(this.parentElement.nextElementSibling.querySelector('textarea').id)">
                🖱️ إدراج رمز "سحب وإفلات" (للتحريك بحرية)
            </button>
            <span style="margin-right:15px; font-size:12px; color:#666;">👈 استخدم خيار (Line Height) في المحرر لتقريب الأسطر</span>
        </div>
        """
        
        content = response.content.decode('utf-8')
        new_content = content.replace('</body>', custom_logic + '</body>')
        new_content = new_content.replace('<div class="django-ckeditor-widget"', tool_html + '<div class="django-ckeditor-widget"')
        
        response.content = new_content.encode('utf-8')
        return response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')

admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
