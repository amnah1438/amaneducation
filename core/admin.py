from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# إعدادات عنوان لوحة التحكم
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"

# كود JavaScript لتفعيل لوحة الرسم والرموز الرياضية
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
                    <h3 style="color:#2d5a27; margin-bottom:15px;">🎨 لوحة الرسم والرموز الرياضية</h3>
                    <math-field id="drawer-field" 
                        style="width:100%; font-size:32px; border:2px solid #2d5a27; border-radius:10px; margin-bottom:20px; padding:15px;"
                        virtual-keyboard-mode="onfocus">
                    </math-field>
                    <div style="display:flex; gap:10px; justify-content:center;">
                        <button id="insert-math" style="background:#2d5a27; color:white; border:none; padding:12px 35px; border-radius:8px; cursor:pointer; font-weight:bold;">✅ إدراج في النص</button>
                        <button id="close-math" style="background:#cc0000; color:white; border:none; padding:12px 35px; border-radius:8px; cursor:pointer; font-weight:bold;">❌ إلغاء</button>
                    </div>
                    <p style="text-align:center; margin-top:15px; font-size:14px; color:#555;">
                        💡 <b>للرسم:</b> انقري داخل المربع الأبيض، ثم اضغطي على <b>أيقونة لوحة المفاتيح</b> الصغيرة واختاري 📝.
                    </p>
                </div>`;
            document.body.appendChild(overlay);

            const mf = document.getElementById('drawer-field');
            setTimeout(() => { 
                mf.focus(); 
                if (window.mathVirtualKeyboard) window.mathVirtualKeyboard.show();
            }, 400);

            document.getElementById('insert-math').onclick = function() {
                if(mf.value) { 
                    editor.insertHtml('\\\\(' + mf.value + '\\\\)'); 
                }
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
                    btn.className = 'math-draw-btn';
                    btn.type = 'button';
                    btn.style = "margin-top:10px; background:#2d5a27; color:white; padding:8px 20px; border-radius:25px; cursor:pointer; border:none; font-weight:bold;";
                    btn.onclick = () => window.openMathDrawer(textareaId);
                    widget.appendChild(btn);
                }
            });
        }
        setTimeout(injectButtons, 2000);
    });
</script>
"""

# تسجيل الأسئلة (Question)
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')
    def render_change_form(self, request, context, **kwargs):
        # تم تصحيح تمرير الـ request هنا
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

# تسجيل المهارات والدروس (Skill)
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    def render_change_form(self, request, context, **kwargs):
        # تم تصحيح تمرير الـ request هنا لتجنب TypeError
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

# تسجيل باقي الأقسام
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
