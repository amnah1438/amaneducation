from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# ================================
# إعدادات واجهة الإدارة
# ================================
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"


# ================================
# كود لوحة الرموز + الرسم (كما عدلناه)
# ================================
MATHLIVE_JS = """
<script src="https://unpkg.com/mathlive/dist/mathlive.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/mathlive/dist/mathlive.core.css">

<script>
document.addEventListener('DOMContentLoaded', function () {

    window.mathVirtualKeyboard.layouts = ['numeric', 'symbols', 'greek'];
    window.mathVirtualKeyboard.visible = false;
    window.mathVirtualKeyboard.policy = 'manual';

    window.openMathDrawer = function(targetId) {

        const editor = CKEDITOR.instances[targetId];

        const overlay = document.createElement('div');
        overlay.id = 'math-overlay';
        overlay.style = `
            position:fixed;
            inset:0;
            background:rgba(0,0,0,0.85);
            z-index:99999;
            display:flex;
            align-items:center;
            justify-content:center;
        `;

        overlay.innerHTML = `
            <div style="
                background:#ffffff;
                padding:25px;
                border-radius:16px;
                width:95%;
                max-width:900px;
                direction:rtl;
                text-align:right;
                box-shadow:0 20px 60px rgba(0,0,0,.5);
            ">

                <h3 style="color:#2d5a27; margin-bottom:10px;">
                    🧮 لوحة الرسم والرموز الرياضية
                </h3>

                <math-field
                    id="mathField"
                    style="
                        width:100%;
                        font-size:32px;
                        border:2px solid #2d5a27;
                        border-radius:12px;
                        padding:15px;
                        margin:15px 0;
                        direction:rtl;
                    "
                    virtual-keyboard-mode="manual"
                ></math-field>

                <div style="display:flex; gap:12px; justify-content:center; margin-top:10px;">
                    <button id="drawBtn"
                        style="background:#0d6efd;color:#fff;padding:10px 25px;border:none;border-radius:10px;cursor:pointer;">
                        ✍️ رسم
                    </button>

                    <button id="insertBtn"
                        style="background:#2d5a27;color:#fff;padding:10px 25px;border:none;border-radius:10px;cursor:pointer;">
                        ✅ إدراج
                    </button>

                    <button id="closeBtn"
                        style="background:#c00;color:#fff;padding:10px 25px;border:none;border-radius:10px;cursor:pointer;">
                        ❌ إلغاء
                    </button>
                </div>

                <p style="font-size:13px;color:#666;text-align:center;margin-top:10px;">
                    💡 اضغطي «رسم» ثم استخدمي الفأرة أو القلم لرسم الجذور والكسور
                </p>
            </div>
        `;

        document.body.appendChild(overlay);

        const mf = document.getElementById('mathField');

        setTimeout(() => {
            mf.focus();
            mathVirtualKeyboard.show();
        }, 300);

        document.getElementById('drawBtn').onclick = () => {
            mf.executeCommand('toggleHandwriting');
        };

        document.getElementById('insertBtn').onclick = () => {
            const latex = mf.getValue('latex');
            if (latex) {
                editor.insertHtml('\\\\(' + latex + '\\\\)');
            }
            overlay.remove();
            mathVirtualKeyboard.hide();
        };

        document.getElementById('closeBtn').onclick = () => {
            overlay.remove();
            mathVirtualKeyboard.hide();
        };
    };

    function injectButtons() {
        document.querySelectorAll('.django-ckeditor-widget').forEach(widget => {

            const textarea = widget.querySelector('textarea');
            if (!textarea || widget.querySelector('.math-btn')) return;

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'math-btn';
            btn.textContent = '🧮 رسم / إدراج معادلة';

            btn.style = `
                margin-top:8px;
                background:#2d5a27;
                color:white;
                padding:8px 16px;
                border-radius:20px;
                border:none;
                cursor:pointer;
                font-weight:bold;
            `;

            btn.onclick = () => openMathDrawer(textarea.id);
            widget.appendChild(btn);
        });
    }

    setTimeout(injectButtons, 1500);
});
</script>
"""


# ================================
# Inline الأسئلة (الإضافة الناقصة)
# ================================
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


# ================================
# Skill Admin (مع الأسئلة + MathLive)
# ================================
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.render()
        response.content = response.content.replace(
            b'</body>',
            MATHLIVE_JS.encode() + b'</body>'
        )
        return response


# ================================
# Question Admin (كما هو + MathLive)
# ================================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.render()
        response.content = response.content.replace(
            b'</body>',
            MATHLIVE_JS.encode() + b'</body>'
        )
        return response


# ================================
# باقي التسجيلات (بدون تغيير)
# ================================
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)