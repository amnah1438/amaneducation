from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# --- إعدادات العناوين ---
admin.site.site_header = "إدارة منصة آمنة التعليمية"
admin.site.index_title = "لوحة التحكم بالعناصر"

# --- كود JavaScript لدمج MathLive ---
MATHLIVE_JS = """
<script src="https://unpkg.com/mathlive"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        window.openMathDrawer = function(targetId) {
            const editor = CKEDITOR.instances[targetId];
            const mathfield = document.createElement('math-field');
            const overlay = document.createElement('div');
            overlay.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; display:flex; flex-direction:column; align-items:center; justify-content:center; color:white;";
            overlay.innerHTML = `
                <div style="background:white; padding:20px; border-radius:10px; width:80%; max-width:600px; text-align:center;">
                    <h3 style="color:#2d5a27;">✍️ ارسم الرمز الرياضي أدناه</h3>
                    <math-field id="drawer-field" style="width:100%; font-size:24px; border:1px solid #ccc; margin-bottom:20px; color:black;"></math-field>
                    <div style="display:flex; gap:10px; justify-content:center;">
                        <button id="insert-math" style="background:#2d5a27; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">إدراج</button>
                        <button id="close-math" style="background:#cc0000; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">إلغاء</button>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);
            const drawerField = document.getElementById('drawer-field');
            document.getElementById('insert-math').onclick = function() {
                if(drawerField.value) editor.insertHtml('\\\\(' + drawerField.value + '\\\\)');
                document.body.removeChild(overlay);
            };
            document.getElementById('close-math').onclick = () => document.body.removeChild(overlay);
        };
        function injectButtons() {
            document.querySelectorAll('.django-ckeditor-widget').forEach(widget => {
                const textareaId = widget.querySelector('textarea').id;
                if (!widget.querySelector('.math-draw-btn')) {
                    const btn = document.createElement('button');
                    btn.innerHTML = '✍️ ارسم رمزاً رياضياً';
                    btn.type = 'button';
                    btn.style = "display:block; margin-top:5px; background:#f8f9fa; border:1px solid #2d5a27; color:#2d5a27; padding:5px; border-radius:4px; cursor:pointer;";
                    btn.onclick = () => window.openMathDrawer(textareaId);
                    widget.appendChild(btn);
                }
            });
        }
        setTimeout(injectButtons, 2000);
    });
</script>
"""

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("title", "category")
    inlines = [QuestionInline]
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.render() # هذا هو السطر الذي يمنع الخطأ
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.render() # السطر السحري هنا أيضاً
        response.content = response.content.replace(b'</body>', MATHLIVE_JS.encode() + b'</body>')
        return response

admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
