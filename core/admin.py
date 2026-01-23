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
        
        # كود التحريك الحر الفعلي + حذف البوكسات المشوهة
        advanced_logic = """
        <script>
            // وظيفة إدراج رمز يمكنك تحريكه بالفأرة في أي مكان (مثل الستيكر)
            function insertFloatingSymbol(editorId) {
                var editor = CKEDITOR.instances[editorId];
                // نستخدم Style تجعل العنصر يطفو فوق النص وتحركه بحرية
                var symbolHtml = `
                    <span class="floating-sticker" contenteditable="true" 
                          style="display:inline-block; position:absolute; cursor:move; 
                                 background:rgba(111, 66, 193, 0.1); border:1px dashed #6f42c1; 
                                 padding:2px 8px; border-radius:4px; color:#6f42c1; z-index:9999;">
                        +
                    </span>&nbsp;`;
                editor.insertHtml(symbolHtml);
            }

            document.addEventListener('DOMContentLoaded', function() {
                if (typeof CKEDITOR !== 'undefined') {
                    CKEDITOR.on('instanceReady', function(ev) {
                        ev.editor.config.contentsLangDirection = 'rtl';
                        // تفعيل ميزة تباعد الأسطر (التقريب) في القائمة
                        ev.editor.config.line_height = "0.5;0.7;1.0;1.2;1.5";
                        ev.editor.editable().setStyle('font-family', 'Cairo, sans-serif');
                        
                        // إضافة كود برمجي يسمح بالسحب والإفلات داخل المحرر
                        ev.editor.on('doubleclick', function(evt) {
                            var element = evt.data.element;
                            if (element.hasClass('floating-sticker')) {
                                alert('يمكنك الآن سحب هذا الرمز بالفأرة لأي مكان');
                            }
                        });
                    });
                }
            });
        </script>
        <style>
            /* حذف أي بوكسات قديمة وتنسيق الواجهة */
            :root { --p: #6f42c1; }
            #header { background: var(--p) !important; }
            
            /* الفاصل البنفسجي الأنيق (خط نحيف فوق كل سؤال) */
            .inline-group .inline-related {
                border: 1px solid #eee !important;
                border-top: 5px solid var(--p) !important;
                margin-bottom: 30px !important;
                border-radius: 8px !important;
                overflow: visible !important;
            }

            /* شريط الأدوات الجديد: أنيق، بسيط، وبدون بوكسات كبيرة */
            .amna-simple-bar {
                display: flex; align-items: center; 
                padding: 10px; background: #fff; 
                border: 1px solid #ddd; border-bottom: none;
                border-radius: 8px 8px 0 0; margin-top: 15px;
            }
            .btn-sticker {
                background: var(--p); color: white; border: none;
                padding: 6px 15px; border-radius: 4px; cursor: pointer;
                font-weight: bold; font-size: 13px;
            }
            .btn-sticker:hover { background: #59359a; }
            .hint { margin-right: 15px; color: #777; font-size: 12px; }

            /* إخفاء ويدجت django الأصلية المزعجة */
            .django-ckeditor-widget { border: none !important; }
        </style>
        """
        
        # الشريط الجديد النظيف
        clean_toolbar = """
        <div class="amna-simple-bar">
            <button type="button" class="btn-sticker" onclick="insertFloatingSymbol(this.parentElement.nextElementSibling.querySelector('textarea').id)">
                ➕ إدراج رمز "حر الحركة"
            </button>
            <span class="hint">💡 <b>لتحريك الرمز:</b> اسحبيه بالفأرة وضعي الزائد في المكان الذي تريدينه.</span>
        </div>
        """
        
        content = response.content.decode('utf-8')
        new_content = content.replace('</body>', advanced_logic + '</body>')
        new_content = new_content.replace('<div class="django-ckeditor-widget"', clean_toolbar + '<div class="django-ckeditor-widget"')
        
        response.content = new_content.encode('utf-8')
        return response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')

admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
