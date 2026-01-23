from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# ================================
# إعدادات واجهة الإدارة
# ================================
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"


# ================================
# كود MathLive + واجهة أنيقة + أرقام عربية
# ================================
MATHLIVE_JS = """
<script src="https://unpkg.com/mathlive/dist/mathlive.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/mathlive/dist/mathlive.core.css">

<style>
.math-btn {
    margin-top:10px;
    background:#1f7a5f;
    color:white;
    padding:10px 18px;
    border-radius:25px;
    border:none;
    cursor:pointer;
    font-weight:bold;
    font-size:14px;
}
.math-btn:hover {
    background:#155c47;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function () {

    // ===== تحويل الأرقام للعربية =====
    function toArabicDigits(text) {
        const map = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];
        return text.replace(/[0-9]/g, d => map[d]);
    }

    // ===== إعدادات لوحة المفاتيح =====
    window.mathVirtualKeyboard.layouts = ['numeric', 'symbols', 'greek'];
    window.mathVirtualKeyboard.policy = 'manual';

    // ===== نافذة المعادلة الأنيقة =====
    window.openMathDrawer = function(targetId) {

        const editor = CKEDITOR.instances[targetId];

        const overlay = document.createElement('div');
        overlay.style = `
            position:fixed;
            inset:0;
            background:rgba(0,0,0,0.35);
            z-index:99999;
            display:flex;
            align-items:center;
            justify-content:center;
        `;

        overlay.innerHTML = `
            <div style="
                background:#fff;
                padding:30px;
                border-radius:20px;
                width:95%;
                max-width:750px;
                direction:rtl;
                font-family:'Tahoma';
            ">
                <h2 style="margin-bottom:10px;color:#1f7a5f;">
                    ✍️ كتابة المعادلة الرياضية
                </h2>

                <p style="font-size:14px;color:#666;">
                    ارسمي الكسر أو الجذر أو اكتبي من لوحة المفاتيح، ثم اضغطي «إدراج»
                </p>

                <math-field id="mathField"
                    style="
                        width:100%;
                        font-size:34px;
                        border:2px solid #1f7a5f;
                        border-radius:14px;
                        padding:18px;
                        margin:15px 0;
                        direction:rtl;
                    "
                    virtual-keyboard-mode="manual">
                </math-field>

                <div style="display:flex; gap:12px; justify-content:center; margin-top:15px;">
                    <button id="drawBtn" class="math-btn">✍️ رسم</button>
                    <button id="kbBtn" class="math-btn">⌨️ لوحة المفاتيح</button>
                    <button id="insertBtn" class="math-btn">✅ إدراج</button>
                    <button id="closeBtn" class="math-btn" style="background:#b00020;">❌ إغلاق</button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        const mf = document.getElementById('mathField');
        mf.focus();

        document.getElementById('drawBtn').onclick = () => {
            mf.executeCommand('toggleHandwriting');
        };

        document.getElementById('kbBtn').onclick = () => {
            mathVirtualKeyboard.show();
        };

        document.getElementById('insertBtn').onclick = () => {
            let latex = mf.getValue('latex');
            let display = toArabicDigits(latex);
            editor.insertHtml('\\\\(' + display + '\\\\)');
            overlay.remove();
            mathVirtualKeyboard.hide();
        };

        document.getElementById('closeBtn').onclick = () => {
            overlay.remove();
            mathVirtualKeyboard.hide();
        };
    };

    // ===== زر الإدراج تحت CKEditor =====
    function injectButtons() {
        document.querySelectorAll('.django-ckeditor-widget').forEach(widget => {
            const textarea = widget.querySelector('textarea');
            if (!textarea || widget.querySelector('.math-btn')) return;

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'math-btn';
            btn.textContent = '🧮 إدراج معادلة رياضية';
            btn.onclick = () => openMathDrawer(textarea.id);
            widget.appendChild(btn);
        });
    }

    const observer = new MutationObserver(() => injectButtons());
    observer.observe(document.body, { childList: true, subtree: true });

});
</script>
"""


# ================================
# Inline الأسئلة (كما طلبتِ)
# ================================
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


# ================================
# Skill Admin
# ================================
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.render()
        response.content = response.content.replace(
            b'</body>', MATHLIVE_JS.encode() + b'</body>'
        )
        return response


# ================================
# Question Admin
# ================================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        response.render()
        response.content = response.content.replace(
            b'</body>', MATHLIVE_JS.encode() + b'</body>'
        )
        return response


# ================================
# باقي التسجيلات (بدون حذف)
# ================================
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)