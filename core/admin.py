from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# كود JavaScript المطور لإظهار زر الرسم وتفعيل الكتابة
MATHLIVE_JS = """
<script src="https://unpkg.com/mathlive"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // إعدادات لوحة المفاتيح لإظهار زر الرسم (Handwriting)
        mathVirtualKeyboard.layouts = {
            default: {
                layers: ['default'],
                controlBar: [
                    { label: 'drawing', command: 'toggleHandwriting', class: 'hide-on-sm' }
                ]
            }
        };

        window.openMathDrawer = function(targetId) {
            const editor = CKEDITOR.instances[targetId];
            const overlay = document.createElement('div');
            overlay.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:9999; display:flex; align-items:center; justify-content:center;";
            
            overlay.innerHTML = `
                <div style="background:white; padding:25px; border-radius:15px; width:95%; max-width:800px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); direction:rtl;">
                    <h3 style="text-align:center; color:#2d5a27; margin-bottom:15px;">🎨 اكتب الرموز أو استخدم زر الرسم أدناه</h3>
                    
                    <math-field id="drawer-field" 
                        style="width:100%; font-size:32px; border:2px solid #2d5a27; border-radius:10px; margin-bottom:20px; padding:15px; background:#f9f9f9;"
                        virtual-keyboard-mode="onfocus"
                        locale="ar">
                    </math-field>

                    <div style="display:flex; gap:15px; justify-content:center;">
                        <button id="insert-math" style="background:#2d5a27; color:white; border:none; padding:12px 35px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:18px;">إدراج في الدرس</button>
                        <button id="close-math" style="background:#cc0000; color:white; border:none; padding:12px 35px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:18px;">إلغاء</button>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);

            const mf = document.getElementById('drawer-field');
            
            // حل مشكلة "عدم الكتابة": ربط الحقل بلوحة المفاتيح فوراً
            setTimeout(() => {
                mf.focus();
                mathVirtualKeyboard.show(); 
            }, 300);

            document.getElementById('insert-math').onclick = function() {
                if(mf.value) {
                    editor.insertHtml('\\\\(' + mf.value + '\\\\)');
                }
                mathVirtualKeyboard.hide();
                document.body.removeChild(overlay);
            };
            document.getElementById('close-math').onclick = () => {
                mathVirtualKeyboard.hide();
                document.body.removeChild(overlay);
            };
        };

        function injectButtons() {
            document.querySelectorAll('.django-ckeditor-widget').forEach(widget => {
                const textareaId = widget.querySelector('textarea').id;
                if (!widget.querySelector('.math-draw-btn')) {
                    const btn = document.createElement('button');
                    btn.innerHTML = '📝 إدراج رموز رياضية (رسم/كتابة)';
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

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    # (بقية إعدادات الموديل الأنيقة التي أرسلتها لكِ سابقاً)
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.render()
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

# تسجيل بقية الموديلات لضمان عمل السيرفر
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
admin.site.register(Question)
