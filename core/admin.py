from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# 1. إعدادات العناوين
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"
admin.site.site_title = "لوحة تحكم آمنة"

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]
    
    fieldsets = (
        ('المعلومات الأساسية', {'fields': ('title', 'category', 'short_description')}),
        ('المحتوى التعليمي', {'fields': ('video_url', 'content_text', 'image_explainer', 'pdf_file')}),
        ('إعدادات إضافية', {'fields': ('card_color',)}),
    )

    def render_change_form(self, request, context, **kwargs):
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        
        # كود التنسيق الجمالي والأدوات الذكية
        custom_style_logic = """
        <script>
            // وظيفة إدراج صندوق نص حر (اكتبي فيه أي رمز وحركيه)
            function insertFreeBox(editorId) {
                var editor = CKEDITOR.instances[editorId];
                var html = '<span class="draggable-item" contenteditable="true" style="display:inline-block; min-width:20px; border:1px dashed #6f42c1; cursor:move; color:#6f42c1; padding:2px; margin:0 5px;">+</span>';
                editor.insertHtml(html);
            }

            document.addEventListener('DOMContentLoaded', function() {
                if (typeof CKEDITOR !== 'undefined') {
                    CKEDITOR.on('instanceReady', function(ev) {
                        ev.editor.config.contentsLangDirection = 'rtl';
                        // تفعيل خيار التقريب (تباعد الأسطر)
                        ev.editor.config.line_height = "0.5;0.7;1.0;1.2;1.5";
                        ev.editor.editable().setStyle('font-family', 'Cairo, sans-serif');
                    });
                }
            });
        </script>
        <style>
            /* --- تحسين المظهر العام بنفسجي ملكي --- */
            :root { --p: #6f42c1; --bg: #fdfbff; }
            #header { background: var(--p) !important; }
            .module h2 { background: #59359a !important; border-radius: 8px 8px 0 0; }
            
            /* --- الفاصل البنفسجي بين الأسئلة (أصبح أنحف وأجمل) --- */
            .inline-group .inline-related {
                border: 1px solid #e0d9f0 !important;
                border-top: 6px solid var(--p) !important;
                margin-bottom: 35px !important;
                border-radius: 10px !important;
                box-shadow: 0 4px 15px rgba(111, 66, 193, 0.05);
            }

            /* --- شريط الأدوات الأنيق فوق المحرر --- */
            .amna-toolbar {
                display: flex; align-items: center; gap: 15px;
                background: var(--bg); padding: 8px 15px;
                border: 1px solid #e0d9f0; border-bottom: none;
                border-radius: 10px 10px 0 0; margin-top: 10px;
            }
            .btn-amna {
                background: var(--p); color: white; border: none;
                padding: 5px 15px; border-radius: 6px; cursor: pointer;
                font-size: 13px; font-weight: bold; transition: 0.2s;
            }
            .btn-amna:hover { background: #59359a; transform: translateY(-1px); }
            .hint-text { color: #888; font-size: 12px; }

            /* إخفاء البوردر القبيح للمحرر القديم */
            .django-ckeditor-widget { border: none !important; }
        </style>
        """
        
        # إضافة الشريط الأنيق قبل كل محرر
        toolbar_html = """
        <div class="amna-toolbar">
            <button type="button" class="btn-amna" onclick="insertFreeBox(this.parentElement.nextElementSibling.querySelector('textarea').id)">
                🖱️ إدراج رمز حر للتحريك
            </button>
            <span class="hint-text">💡 للتقريب: استخدمي أيقونة المسافات في شريط الأدوات بالأعلى.</span>
        </div>
        """
        
        content = response.content.decode('utf-8')
        new_content = content.replace('</body>', custom_style_logic + '</body>')
        new_content = new_content.replace('<div class="django-ckeditor-widget"', toolbar_html + '<div class="django-ckeditor-widget"')
        
        response.content = new_content.encode('utf-8')
        return response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')

admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
