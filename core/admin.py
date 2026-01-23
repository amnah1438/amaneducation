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
        
        # كود لإعادة الألوان وتفعيل ميزة التقريب داخل شريط الأدوات
        custom_logic = """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                if (typeof CKEDITOR !== 'undefined') {
                    CKEDITOR.on('instanceReady', function(ev) {
                        ev.editor.config.contentsLangDirection = 'rtl';
                        // إضافة خيار تقريب الأسطر (Line Height) داخل أدوات المحرر
                        ev.editor.config.extraPlugins = 'lineheight';
                        ev.editor.config.line_height = "0.5;0.8;1.0;1.5;2.0";
                        ev.editor.editable().setStyle('font-family', 'Cairo, sans-serif');
                    });
                }
            });
        </script>
        <style>
            /* 1. إعادة الألوان والتمييز بين الأسئلة */
            :root { --amna-purple: #6f42c1; }
            
            .inline-group .inline-related {
                border: 1px solid #e0d9f0 !important;
                border-top: 10px solid var(--amna-purple) !important; /* فاصل بنفسجي سميك وواضح */
                margin-bottom: 40px !important;
                border-radius: 12px !important;
                background: #fdfbff !important; /* خلفية فاتحة جداً لكل سؤال */
                box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
            }

            .inline-group .inline-related h3 {
                background: var(--amna-purple) !important;
                color: white !important;
                border-radius: 5px 5px 0 0 !important;
            }

            /* 2. حذف أي أزرار خارجية أو بوكسات كانت موجودة سابقاً */
            .amna-mini-tools, .amna-bar, .mini-tools, .btn-sticker {
                display: none !important;
            }
            
            /* تحسين شكل الحقول داخل المحرر */
            .django-ckeditor-widget { width: 100% !important; border: 1px solid #ccc !important; }
        </style>
        """
        
        content = response.content.decode('utf-8')
        new_content = content.replace('</body>', custom_logic + '</body>')
        
        response.content = new_content.encode('utf-8')
        return response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')

admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
