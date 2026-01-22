from django.contrib import admin
from django import forms
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# --- تنظيف العناوين الرئيسية ---
admin.site.site_header = "إدارة منصة آمنة التعليمية"
admin.site.index_title = "لوحة التحكم بالعناصر"

# --- كود JavaScript لدمج MathLive والتعرف على الرسم ---
MATHLIVE_JS = """
<script src="https://unpkg.com/mathlive"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // وظيفة لفتح لوحة الرسم وربطها بالمحرر
        window.openMathDrawer = function(targetId) {
            const editor = CKEDITOR.instances[targetId];
            const mathfield = new MathfieldElement();
            
            // إنشاء نافذة منبثقة بسيطة للرسم
            const overlay = document.createElement('div');
            overlay.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; display:flex; flex-direction:column; align-items:center; justify-content:center; color:white; font-family:sans-serif;";
            overlay.innerHTML = `
                <div style="background:white; padding:20px; border-radius:10px; width:80%; max-width:600px; text-align:center;">
                    <h3 style="color:#2d5a27;">✍️ ارسم الرمز الرياضي أدناه</h3>
                    <math-field id="drawer-field" style="width:100%; font-size:24px; border:1px solid #ccc; margin-bottom:20px;"></math-field>
                    <div style="display:flex; gap:10px; justify-content:center;">
                        <button id="insert-math" style="background:#2d5a27; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">إدراج في السؤال</button>
                        <button id="close-math" style="background:#cc0000; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">إلغاء</button>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);

            const drawerField = document.getElementById('drawer-field');
            
            // زر الإدراج
            document.getElementById('insert-math').onclick = function() {
                const latex = drawerField.value;
                if(latex) {
                    editor.insertHtml('\\\\(' + latex + '\\\\)'); // إدراج الرمز بصيغة يفهمها MathJax
                }
                document.body.removeChild(overlay);
            };

            // زر الإغلاق
            document.getElementById('close-math').onclick = function() {
                document.body.removeChild(overlay);
            };
        };

        // إضافة أزرار "ارسم" تحت المحررات بشكل آلي
        function injectButtons() {
            const editors = document.querySelectorAll('.django-ckeditor-widget');
            editors.forEach(widget => {
                const textareaId = widget.querySelector('textarea').id;
                if (!widget.querySelector('.math-draw-btn')) {
                    const btn = document.createElement('button');
                    btn.innerHTML = '✍️ ارسم رمزاً رياضياً (MathLive)';
                    btn.type = 'button';
                    btn.className = 'math-draw-btn';
                    btn.style = "display:block; margin-top:5px; background:#f8f9fa; border:1px solid #2d5a27; color:#2d5a27; padding:5px 10px; border-radius:4px; cursor:pointer; font-weight:bold;";
                    btn.onclick = () => window.openMathDrawer(textareaId);
                    widget.appendChild(btn);
                }
            });
        }
        
        // تشغيل الحقن بعد تحميل المحرر
        setTimeout(injectButtons, 2000);
    });
</script>
<style>
    .math-draw-btn:hover { background: #2d5a27 !important; color: white !important; }
</style>
"""

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1  
    fieldsets = (
        (None, {
            'fields': ('test_type', 'question_text'),
        }),
        ('خيارات الإجابة', {
            'fields': (
                ('option_a', 'option_b'),
                ('option_c', 'option_d'),
            ),
        }),
        ('النتيجة والتغذية الراجعة', {
            'fields': ('correct_answer', 'feedback'),
        }),
    )

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "get_teachers", "required_questions_count")
    list_filter = ("category",)
    filter_horizontal = ("teachers",) 
    inlines = [QuestionInline]
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'category', 'teachers', 'required_questions_count')
        }),
        ('محتوى الشرح (مرونة المعلمة)', {
            'fields': ('content_text', 'video_url', 'pdf_file', 'image_explainer'),
        }),
        ('تنسيق البطاقة (الإعدادات البصرية)', {
            'fields': ('icon_image', 'short_description', 'card_color'),
            'classes': ('collapse',), 
        }),
    )

    def get_teachers(self, obj):
        return ", ".join([t.name for t in obj.teachers.all()])
    get_teachers.short_description = "المعلمات المسؤولات"

    # حقن كود الرسم في صفحة المهارات
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "skill", "test_type", "correct_answer")
    list_filter = ("test_type", "skill")
    
    # حقن كود الرسم في صفحة الأسئلة المنفردة
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

# تسجيل الموديلات الباقية
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
