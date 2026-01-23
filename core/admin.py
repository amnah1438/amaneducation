from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]
    
    def render_change_form(self, request, context, **kwargs):
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        
        # كود الأدوات الصغيرة والتقريب التلقائي
        final_script = """
        <script>
            // 1. وظيفة التقريب (تجبر الأسطر على الالتصاق ببعضها)
            function forceTightLines(editorId) {
                var editor = CKEDITOR.instances[editorId];
                var content = editor.getData();
                // نغلف المحتوى بـ div يقلل المسافات جداً
                var newContent = '<div style="line-height: 0.6; font-size: 22px;">' + content + '</div>';
                editor.setData(newContent);
            }

            // 2. وظيفة الرمز الحر (يتحرك ويثبت في أي مكان)
            function addMovableSymbol(editorId) {
                var editor = CKEDITOR.instances[editorId];
                // الرمز الآن يوضع كـ "ملصق" شفاف لا يؤثر على النص
                var sticker = '<span contenteditable="true" style="display:inline-block; cursor:move; color:#6f42c1; font-weight:bold; position:relative; top:0; right:0; padding:0 5px; border:1px solid #e0d9f0;">+</span>';
                editor.insertHtml(sticker);
            }

            document.addEventListener('DOMContentLoaded', function() {
                if (typeof CKEDITOR !== 'undefined') {
                    CKEDITOR.on('instanceReady', function(ev) {
                        ev.editor.config.contentsLangDirection = 'rtl';
                        ev.editor.editable().setStyle('font-family', 'Cairo, sans-serif');
                    });
                }
            });
        </script>
        <style>
            :root { --p: #6f42c1; }
            /* إخفاء البوكسات القبيحة تماماً */
            .inline-group .inline-related { border: 1px solid #ddd !important; border-top: 4px solid var(--p) !important; margin-bottom: 20px !important; border-radius: 8px !important; }

            /* تحويل الأزرار إلى أيقونات صغيرة جداً وأنيقة */
            .amna-mini-tools {
                display: inline-flex; gap: 5px; margin-bottom: -1px; margin-top: 10px;
            }
            .mini-tool-btn {
                background: #fff; border: 1px solid #ddd; color: var(--p);
                padding: 2px 10px; border-radius: 4px 4px 0 0; cursor: pointer;
                font-size: 11px; font-weight: bold; border-bottom: none;
            }
            .mini-tool-btn:hover { background: var(--p); color: #fff; border-color: var(--p); }
            
            /* تنظيف واجهة المحرر */
            .django-ckeditor-widget { border: none !important; width: 100% !important; }
        </style>
        """
        
        # الأدوات الجديدة على شكل ألسنة صغيرة (Tabs) فوق المحرر
        tabs_html = """
        <div class="amna-mini-tools">
            <button type="button" class="mini-tool-btn" onclick="addMovableSymbol(this.parentElement.nextElementSibling.querySelector('textarea').id)">➕ إدراج رمز</button>
            <button type="button" class="mini-tool-btn" onclick="forceTightLines(this.parentElement.nextElementSibling.querySelector('textarea').id)">↕️ تقريب الأسطر فوراً</button>
        </div>
        """
        
        content = response.content.decode('utf-8')
        new_content = content.replace('</body>', final_script + '</body>')
        new_content = new_content.replace('<div class="django-ckeditor-widget"', tabs_html + '<div class="django-ckeditor-widget"')
        
        response.content = new_content.encode('utf-8')
        return response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')

admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
