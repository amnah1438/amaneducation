from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# --- إعدادات عناوين لوحة الإدارة ---
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"
admin.site.index_title = "لوحة التحكم بالمحتوى"

# --- كود JavaScript المطور (الذي طلبته بالأمس) ---
MATHLIVE_JS = """
<script src="https://unpkg.com/mathlive"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        window.openMathDrawer = function(targetId) {
            const editor = CKEDITOR.instances[targetId];
            const overlay = document.createElement('div');
            overlay.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; display:flex; align-items:center; justify-content:center;";
            
            overlay.innerHTML = `
                <div style="background:white; padding:20px; border-radius:15px; width:90%; max-width:600px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                    <h3 style="text-align:center; color:#2d5a27; font-family:sans-serif;">✨ لوحة الرموز الرياضية</h3>
                    
                    <math-field id="drawer-field" 
                        style="width:100%; font-size:28px; border:2px solid #2d5a27; border-radius:8px; margin-bottom:20px; padding:10px;"
                        virtual-keyboard-mode="onfocus"
                        locale="ar">
                    </math-field>

                    <div style="display:flex; gap:10px; justify-content:center;">
                        <button id="insert-math" style="background:#2d5a27; color:white; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold;">إدراج</button>
                        <button id="close-math" style="background:#cc0000; color:white; border:none; padding:12px 25px; border-radius:8px; cursor:pointer; font-weight:bold;">إلغاء</button>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);

            // تفعيل الحقل فوراً عند الفتح ليقبل الكتابة وتظهر لوحة المفاتيح
            const mf = document.getElementById('drawer-field');
            setTimeout(() => mf.focus(), 100);

            document.getElementById('insert-math').onclick = function() {
                if(mf.value) {
                    // إدراج الرمز بصيغة LaTeX ليفهمها المتصفح لاحقاً
                    editor.insertHtml('\\\\(' + mf.value + '\\\\)');
                }
                document.body.removeChild(overlay);
            };
            document.getElementById('close-math').onclick = () => document.body.removeChild(overlay);
        };

        // حقن أزرار الفتح تحت كل محرر نصوص CKEditor
        function injectButtons() {
            document.querySelectorAll('.django-ckeditor-widget').forEach(widget => {
                const textareaId = widget.querySelector('textarea').id;
                if (!widget.querySelector('.math-draw-btn')) {
                    const btn = document.createElement('button');
                    btn.innerHTML = '✍️ إدراج رموز رياضية';
                    btn.type = 'button';
                    btn.style = "margin-top:8px; background:#f0f7f0; border:1px solid #2d5a27; color:#2d5a27; padding:6px 15px; border-radius:20px; cursor:pointer; font-size:12px; font-weight:bold;";
                    btn.onclick = () => window.openMathDrawer(textareaId);
                    widget.appendChild(btn);
                }
            });
        }
        setTimeout(injectButtons, 2000);
    });
</script>
"""

# --- تنسيق عرض الأسئلة داخل صفحة المهارة ---
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    classes = ['collapse']
    verbose_name = "سؤال تدريبي"
    verbose_name_plural = "🧩 بنك الأسئلة"

# --- التنسيق الأنيق لصفحة المهارة (Skill) ---
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'required_questions_count')
    list_filter = ('category', 'teachers')
    
    # تقسيم الحقول إلى مجموعات منظمة (Fieldsets)
    fieldsets = (
        ('📌 المعلومات الأساسية', {
            'fields': ('title', 'category', 'teachers', 'required_questions_count')
        }),
        ('📖 محتوى الشرح', {
            'fields': ('content_text', 'video_url', 'pdf_file', 'image_explainer'),
        }),
        ('🎨 تنسيق البطاقة (اختياري)', {
            'fields': ('icon_image', 'card_color', 'short_description'),
            'classes': ('collapse',), 
        }),
    )
    
    inlines = [QuestionInline]

    # دمج كود الـ JavaScript وحل مشكلة Render Error
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.render() 
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

# تسجيل الموديلات المتبقية
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
