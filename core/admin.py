from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# 1. إعدادات عنوان لوحة التحكم
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"

# 2. كود لوحة الرسم والرموز الرياضية (MathLive)
MATHLIVE_JS = """
<script src="https://unpkg.com/mathlive"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        window.openMathDrawer = function(targetId) {
            const editor = CKEDITOR.instances[targetId];
            const overlay = document.createElement('div');
            overlay.id = "math-overlay";
            overlay.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; display:flex; align-items:center; justify-content:center;";
            overlay.innerHTML = `
                <div style="background:white; padding:25px; border-radius:15px; width:95%; max-width:800px; direction:rtl; text-align:right;">
                    <h3 style="color:#2d5a27;">🎨 لوحة الرسم والرموز الرياضية</h3>
                    <math-field id="drawer-field" style="width:100%; font-size:32px; border:2px solid #2d5a27; border-radius:10px; margin-bottom:15px; padding:15px;" virtual-keyboard-mode="onfocus"></math-field>
                    <div style="display:flex; gap:10px; justify-content:center;">
                        <button id="insert-math" style="background:#2d5a27; color:white; border:none; padding:10px 30px; border-radius:8px; cursor:pointer; font-weight:bold;">✅ إدراج</button>
                        <button id="close-math" style="background:#cc0000; color:white; border:none; padding:10px 30px; border-radius:8px; cursor:pointer; font-weight:bold;">❌ إلغاء</button>
                    </div>
                </div>`;
            document.body.appendChild(overlay);
            const mf = document.getElementById('drawer-field');
            setTimeout(() => { mf.focus(); if (window.mathVirtualKeyboard) window.mathVirtualKeyboard.show(); }, 400);
            document.getElementById('insert-math').onclick = function() {
                if(mf.value) { editor.insertHtml('\\\\(' + mf.value + '\\\\)'); }
                document.getElementById('math-overlay').remove();
            };
            document.getElementById('close-math').onclick = () => document.getElementById('math-overlay').remove();
        };
        function injectButtons() {
            document.querySelectorAll('.django-ckeditor-widget').forEach(widget => {
                const textareaId = widget.querySelector('textarea').id;
                if (!widget.querySelector('.math-draw-btn')) {
                    const btn = document.createElement('button');
                    btn.innerHTML = '📝 رسم أو إدراج رموز رياضية';
                    btn.type = 'button';
                    btn.style = "margin: 10px 0; background:#2d5a27; color:white; padding:8px 15px; border-radius:20px; border:none; cursor:pointer; font-weight:bold;";
                    btn.onclick = () => window.openMathDrawer(textareaId);
                    widget.appendChild(btn);
                }
            });
        }
        setTimeout(injectButtons, 2000);
    });
</script>
"""

# 3. تفعيل إضافة الأسئلة داخل صفحة المهارة (Inline)
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

# 4. تسجيل قسم المهارات (Skill) مع الأسئلة المدمجة
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline] # لربط الأسئلة بالمهارة في نفس الصفحة
    
    def render_change_form(self, request, context, **kwargs):
        # تصحيح الـ request لتجنب الخطأ السابق
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

# 5. تسجيل قسم الأسئلة (Question) ليعود للقائمة الجانبية (تمت إعادته هنا)
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')
    def render_change_form(self, request, context, **kwargs):
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

# 6. تسجيل باقي الأقسام الأساسية
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
