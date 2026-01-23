from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# ================================
# إعدادات واجهة الإدارة
# ================================
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"


# ================================
# MathLive + زر واحد ثابت + رسم فعلي
# ================================
MATHLIVE_JS = """
<script src="https://unpkg.com/mathlive/dist/mathlive.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/mathlive/dist/mathlive.core.css">

<style>
#global-math-bar {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: #f8f9fa;
    padding: 10px;
    text-align: center;
    border-bottom: 1px solid #ddd;
}
#global-math-bar button {
    background: #1f7a5f;
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 25px;
    font-weight: bold;
    cursor: pointer;
}
#global-math-bar button:hover {
    background: #155c47;
}
</style>

<script>
(function() {

    let activeEditor = null;

    // تحويل الأرقام إلى عربية
    function toArabicDigits(text) {
        const map = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];
        return text.replace(/[0-9]/g, d => map[d]);
    }

    // =========================
    // إضافة زر واحد أعلى الصفحة
    // =========================
    function addGlobalButton() {
        if (document.getElementById('global-math-bar')) return;

        const bar = document.createElement('div');
        bar.id = 'global-math-bar';

        const btn = document.createElement('button');
        btn.textContent = '✍️ رسم وكتابة معادلة رياضية';

        btn.onclick = function() {
            if (!activeEditor) {
                alert('⚠️ الرجاء الضغط داخل مربع النص أولاً');
                return;
            }
            openMathDrawer(activeEditor);
        };

        bar.appendChild(btn);
        document.body.prepend(bar);
    }

    // =========================
    // نافذة المعادلة (مفعّلة فعليًا)
    // =========================
    function openMathDrawer(editor) {

        const overlay = document.createElement('div');
        overlay.style = `
            position:fixed;
            inset:0;
            background:rgba(0,0,0,0.35);
            z-index:100000;
            display:flex;
            align-items:center;
            justify-content:center;
        `;

        overlay.innerHTML = `
            <div style="
                background:#fff;
                padding:30px;
                border-radius:20px;
                width:90%;
                max-width:720px;
                direction:rtl;
                font-family:tahoma;
            ">
                <h2 style="color:#1f7a5f;margin-bottom:10px">
                    ✍️ كتابة المعادلة الرياضية
                </h2>

                <div id="mathFieldContainer"
                    style="
                        width:100%;
                        min-height:70px;
                        font-size:34px;
                        border:2px solid #1f7a5f;
                        border-radius:14px;
                        padding:18px;
                        margin:15px 0;
                    ">
                </div>

                <div style="display:flex;gap:12px;justify-content:center">
                    <button id="drawBtn">✍️ رسم</button>
                    <button id="kbBtn">⌨️ لوحة مفاتيح</button>
                    <button id="insertBtn">✅ إدراج</button>
                    <button id="closeBtn" style="background:#b00020;color:white">❌ إغلاق</button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);

        // ⭐ التهيئة الصحيحة لـ MathLive
        const mf = MathLive.makeMathField(
            document.getElementById('mathFieldContainer'),
            {
                virtualKeyboardMode: 'manual',
                locale: 'ar',
                direction: 'rtl'
            }
        );

        document.getElementById('drawBtn').onclick = () => {
            mf.executeCommand('toggleHandwriting');
        };

        document.getElementById('kbBtn').onclick = () => {
            MathLive.virtualKeyboard.show();
        };

        document.getElementById('insertBtn').onclick = () => {
            let latex = mf.getValue('latex');
            latex = toArabicDigits(latex);
            editor.insertHtml('\\\\(' + latex + '\\\\)');
            overlay.remove();
            MathLive.virtualKeyboard.hide();
        };

        document.getElementById('closeBtn').onclick = () => {
            overlay.remove();
            MathLive.virtualKeyboard.hide();
        };
    }

    // =========================
    // تتبع المحرر النشط
    // =========================
    function trackEditors() {
        if (!window.CKEDITOR) return;

        for (const name in CKEDITOR.instances) {
            const editor = CKEDITOR.instances[name];
            if (editor._mathTracked) continue;

            editor.on('focus', function() {
                activeEditor = editor;
            });

            editor._mathTracked = true;
        }
    }

    // مراقبة تحميل الصفحة
    const observer = new MutationObserver(() => {
        addGlobalButton();
        trackEditors();
    });

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
# باقي التسجيلات (بدون حذف)
# ================================
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)