from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# --- إعدادات لوحة الإدارة ---
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"

# --- كود الرموز والكسور والرسم ---
MATHLIVE_JS = """
<script src="https://unpkg.com/mathlive"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        mathVirtualKeyboard.layouts = 'default'; 
        window.openMathDrawer = function(targetId) {
            const editor = CKEDITOR.instances[targetId];
            const overlay = document.createElement('div');
            overlay.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; display:flex; align-items:center; justify-content:center;";
            overlay.innerHTML = `
                <div style="background:white; padding:25px; border-radius:15px; width:95%; max-width:800px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); direction:rtl;">
                    <h3 style="text-align:center; color:#2d5a27;">🎨 ارسم أو اكتب الرمز الرياضي</h3>
                    <math-field id="drawer-field" style="width:100%; font-size:32px; border:2px solid #2d5a27; border-radius:10px; margin-bottom:20px; padding:15px; background:#f9f9f9;" virtual-keyboard-mode="onfocus" locale="ar"></math-field>
                    <div style="display:flex; gap:15px; justify-content:center;">
                        <button id="insert-math" style="background:#2d5a27; color:white; border:none; padding:12px 35px; border-radius:8px; cursor:pointer; font-weight:bold;">✅ إدراج</button>
                        <button id="close-math" style="background:#cc0000; color:white; border:none; padding:12px 35px; border-radius:8px; cursor:pointer; font-weight:bold;">❌ إلغاء</button>
                    </div>
                </div>`;
            document.body.appendChild(overlay);
            const mf = document.getElementById('drawer-field');
            setTimeout(() => { mf.focus(); mathVirtualKeyboard.show(); }, 300);
            document.getElementById('insert-math').onclick = function() {
                if(mf.value) editor.insertHtml('\\\\(' + mf.value + '\\\\)');
                document.body.removeChild(overlay);
            };
            document.getElementById('close-math').onclick = () => { mathVirtualKeyboard.hide(); document.body.removeChild(overlay); };
        };
        function injectButtons() {
            document.querySelectorAll('.django-ckeditor-widget').forEach(widget => {
                const textareaId = widget.querySelector('textarea').id;
                if (!widget.querySelector('.math-draw-btn')) {
                    const btn = document.createElement('button');
                    btn.innerHTML = '📝 رسم/إدراج رموز رياضية';
                    btn.type = 'button';
                    btn.style = "margin-top:10px; background:#2d5a27; color:white; padding:8px 20px; border-radius:25px; cursor:pointer; font-weight:bold; border:none;";
                    btn.onclick = () => window.openMathDrawer(textareaId);
                    widget.appendChild(btn);
                }
            });
        }
        setTimeout(injectButtons, 2000);
    });
</script>
"""

# --- إدارة الأسئلة (Inline) داخل المهارة ---
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    classes = ['collapse']
    verbose_name = "سؤال"
    verbose_name_plural = "🧩 إضافة أسئلة للدرس مباشرة"

# --- إدارة المهارات (Skill) ---
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    fieldsets = (
        ('📌 البيانات الأساسية', {'fields': ('title', 'category', 'teachers', 'required_questions_count')}),
        ('📖 محتوى الدرس (الشرح)', {'fields': ('content_text', 'video_url', 'pdf_file', 'image_explainer')}),
        ('🎨 مظهر البطاقة', {'fields': ('icon_image', 'card_color', 'short_description'), 'classes': ('collapse',)}),
    )
    inlines = [QuestionInline]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.render()
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

# --- إدارة الأسئلة (Question) بشكل مستقل ---
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('skill', 'question_text')
    list_filter = ('skill',)
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.render()
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

# تسجيل الموديلات الأخرى
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
