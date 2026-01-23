from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"

# =====================================
# MathJax + منشئ معادلات للمعلمات
# =====================================
MATH_BUILDER_JS = """
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

<style>
#math-builder-bar {
    position: fixed;
    top: 10px;
    left: 10px;
    z-index: 9999;
}
#math-builder-bar button {
    background:#1f7a5f;
    color:white;
    border:none;
    padding:10px 22px;
    border-radius:25px;
    font-weight:bold;
    cursor:pointer;
}
.math-modal input {
    width:100%;
    padding:6px;
    margin:4px 0;
}
.math-modal button {
    margin-top:6px;
}
</style>

<script>
(function(){

let activeEditor = null;

// تحويل الأرقام إلى عربية
function toArabicDigits(text) {
    const map = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];
    return text.replace(/[0-9]/g, d => map[d]);
}

// =======================
// نافذة منشئ المعادلات
// =======================
function openMathBuilder() {
    if (!activeEditor) {
        alert('اضغطي داخل مربع السؤال أولًا');
        return;
    }

    const overlay = document.createElement('div');
    overlay.style = `
        position:fixed; inset:0;
        background:rgba(0,0,0,0.4);
        z-index:100000;
        display:flex; align-items:center; justify-content:center;
    `;

    overlay.innerHTML = `
        <div class="math-modal"
             style="background:#fff;padding:20px;border-radius:15px;width:420px;direction:rtl">
            <h3>🧮 إنشاء معادلة رياضية</h3>

            <hr>
            <b>➗ كسر</b>
            <input id="fracTop" placeholder="البسط">
            <input id="fracBottom" placeholder="المقام">
            <button onclick="insertFraction()">إدراج كسر</button>

            <hr>
            <b>√ جذر</b>
            <input id="sqrtVal" placeholder="داخل الجذر">
            <button onclick="insertSqrt()">إدراج جذر</button>

            <hr>
            <b>⬆️ أس</b>
            <input id="powBase" placeholder="الأساس">
            <input id="powExp" placeholder="الأس">
            <button onclick="insertPower()">إدراج أس</button>

            <hr>
            <button onclick="closeBuilder()" style="background:#b00020;color:white">
                إغلاق
            </button>
        </div>
    `;

    document.body.appendChild(overlay);

    // ===== وظائف الإدراج =====
    window.insertFraction = function() {
        const a = toArabicDigits(document.getElementById('fracTop').value);
        const b = toArabicDigits(document.getElementById('fracBottom').value);
        activeEditor.insertHtml('\\\\(\\\\frac{' + a + '}{' + b + '}\\\\)');
        closeBuilder();
    };

    window.insertSqrt = function() {
        const a = toArabicDigits(document.getElementById('sqrtVal').value);
        activeEditor.insertHtml('\\\\(\\\\sqrt{' + a + '}\\\\)');
        closeBuilder();
    };

    window.insertPower = function() {
        const a = toArabicDigits(document.getElementById('powBase').value);
        const b = toArabicDigits(document.getElementById('powExp').value);
        activeEditor.insertHtml('\\\\(' + a + '^{' + b + '}\\\\)');
        closeBuilder();
    };

    window.closeBuilder = function() {
        overlay.remove();
    };
}

// =======================
// زر واحد ثابت
// =======================
function addButton() {
    if (document.getElementById('math-builder-bar')) return;

    const bar = document.createElement('div');
    bar.id = 'math-builder-bar';

    const btn = document.createElement('button');
    btn.textContent = '🧮 إدراج معادلة';
    btn.onclick = openMathBuilder;

    bar.appendChild(btn);
    document.body.appendChild(bar);
}

// =======================
// تتبع المحرر النشط
// =======================
function trackEditors() {
    if (!window.CKEDITOR) return;

    for (const name in CKEDITOR.instances) {
        const ed = CKEDITOR.instances[name];
        if (ed._tracked) continue;

        ed.on('focus', function(){
            activeEditor = ed;
        });
        ed._tracked = true;
    }
}

// مراقبة الصفحة
const observer = new MutationObserver(() => {
    addButton();
    trackEditors();
});
observer.observe(document.body, { childList:true, subtree:true });

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
    inlines = [QuestionInline]

    def render_change_form(self, request, context, *args, **kwargs):
        response = super().render_change_form(request, context, *args, **kwargs)
        response.render()
        response.content = response.content.replace(
            b'</body>', MATH_BUILDER_JS.encode() + b'</body>'
        )
        return response

# ================================
# Question Admin
# ================================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    def render_change_form(self, request, context, *args, **kwargs):
        response = super().render_change_form(request, context, *args, **kwargs)
        response.render()
        response.content = response.content.replace(
            b'</body>', MATH_BUILDER_JS.encode() + b'</body>'
        )
        return response

# ================================
# باقي التسجيلات
# ================================
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)