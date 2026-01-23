from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# ================================
# إعدادات واجهة الإدارة
# ================================
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"


# ================================
# MathLive + زر ثابت داخل CKEditor
# ================================
MATHLIVE_JS = """
<script src="https://unpkg.com/mathlive/dist/mathlive.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/mathlive/dist/mathlive.core.css">

<style>
.math-toolbar {
    margin-bottom: 8px;
}
.math-toolbar button {
    background: #1f7a5f;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-weight: bold;
}
.math-toolbar button:hover {
    background: #155c47;
}
</style>

<script>
(function() {

    // تحويل الأرقام إلى عربية
    function toArabicDigits(text) {
        const map = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];
        return text.replace(/[0-9]/g, d => map[d]);
    }

    // نافذة المعادلة
    function openMathDrawer(editor) {

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
                padding:28px;
                border-radius:20px;
                width:90%;
                max-width:700px;
                direction:rtl;
                font-family:tahoma;
            ">
                <h2 style="color:#1f7a5f;margin-bottom:8px;">
                    ✍️ كتابة المعادلة الرياضية
                </h2>

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

                <div style="display:flex;gap:10px;justify-content:center">
                    <button id="drawBtn">✍️ رسم</button>
                    <button id="kbBtn">⌨️ لوحة مفاتيح</button>
                    <button id="insertBtn">✅ إدراج</button>
                    <button id="closeBtn" style="background:#b00020">❌ إغلاق</button>
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
            latex = toArabicDigits(latex);
            editor.insertHtml('\\\\(' + latex + '\\\\)');
            overlay.remove();
            mathVirtualKeyboard.hide();
        };

        document.getElementById('closeBtn').onclick = () => {
            overlay.remove();
            mathVirtualKeyboard.hide();
        };
    }

    // ربط الزر مباشرة مع CKEditor
    function attachMathButton() {
        if (!window.CKEDITOR) return;

        for (const name in CKEDITOR.instances) {
            const editor = CKEDITOR.instances[name];
            if (editor.mathAttached) continue;

            editor.on('instanceReady', function() {
                const container = editor.container.$;
                if (container.querySelector('.math-toolbar')) return;

                const bar = document.createElement('div');
                bar.className = 'math-toolbar';
                bar.innerHTML = '<button type="button">✍️ رسم وكتابة معادلة رياضية</button>';
                bar.querySelector('button').onclick = () => openMathDrawer(editor);

                container.parentNode.insertBefore(bar, container);
                editor.mathAttached = true;
            });
        }
    }

    // مراقبة تحميل CKEditor
    const observer = new MutationObserver(() => attachMathButton());
    observer.observe(document.body, { childList: true, subtree: true });

})();
</script>
"""


# ================================
# Inline الأسئلة
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
# باقي التسجيلات (كما هي)
# ================================
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)