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
        
        custom_logic = """
        <script>
            // وظيفة تقريب الأسطر (تباعد صغير جداً)
            function shrinkLines(editorId) {
                var editor = CKEDITOR.instances[editorId];
                var style = new CKEDITOR.style({ element: 'div', attributes: { 'style': 'line-height:0.6;' } });
                editor.applyStyle(style);
            }

            // وظيفة إدراج رمز حر وقابل للسحب
            function insertDraggableIcon(editorId) {
                var editor = CKEDITOR.instances[editorId];
                // نستخدم خاصية draggable و absolute للتحريك
                var html = '<span class="movable" contenteditable="true" draggable="true" ondragstart="event.dataTransfer.setData(\'text/plain\',null)" style="display:inline-block; cursor:move; color:#6f42c1; font-weight:bold; position:relative; padding:2px; border:1px dashed #ddd;">+</span>&nbsp;';
                editor.insertHtml(html);
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
            #header { background: var(--p) !important; }
            
            /* فاصل بنفسجي أنيق ونحيف */
            .inline-group .inline-related {
                border: 1px solid #ddd !important;
                border-top: 5px solid var(--p) !important;
                margin-bottom: 25px !important;
                border-radius: 8px !important;
            }

            /* تحويل البوكس الكبير إلى أيقونات صغيرة أنيقة فوق المحرر */
            .mini-tools {
                display: flex; gap: 8px; padding: 5px; 
                background: #fff; border: 1px solid #eee; border-bottom: none;
                border-radius: 5px 5px 0 0; width: fit-content; margin-top: 10px;
            }
            .tool-icon {
                background: #f8f6fc; border: 1px solid var(--p); color: var(--p);
                padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: bold;
            }
            .tool-icon:hover { background: var(--p); color: white; }
            .django-ckeditor-widget { border: none !important; }
        </style>
        """
        
        # الأيقونات الصغيرة الجديدة
        mini_toolbar = """
        <div class="mini-tools">
            <button type="button" class="tool-icon" title="إدراج رمز للتحريك" onclick="insertDraggableIcon(this.parentElement.nextElementSibling.querySelector('textarea').id)">➕ رمز حر</button>
            <button type="button" class="tool-icon" title="تقريب الأسطر من بعضها" onclick="shrinkLines(this.parentElement.nextElementSibling.querySelector('textarea').id)">↕️ تقريب الأسطر</button>
        </div>
        """
        
        content = response.content.decode('utf-8')
        new_content = content.replace('</body>', custom_logic + '</body>')
        new_content = new_content.replace('<div class="django-ckeditor-widget"', mini_toolbar + '<div class="django-ckeditor-widget"')
        
        response.content = new_content.encode('utf-8')
        return response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')

admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
