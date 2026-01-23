from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# 1. إعدادات رأس الصفحة
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"

# 2. كود محرر الرياضيات العربي الخاص (يظهر فوق صناديق النصوص)
ARABIC_MATH_JS = """
<script>
    function insertArabicMath(editorId, type) {
        var editor = CKEDITOR.instances[editorId];
        var content = "";
        
        if (type === 'fraction') {
            // كسر عربي: بسط ومقام مع خط بينهما
            content = '<span style="display:inline-block; vertical-align:middle; text-align:center; direction:rtl; font-family:Arial;">' +
                      '<div style="border-bottom:1px solid #000; padding:0 5px;">البسط</div>' +
                      '<div>المقام</div></span>&nbsp;';
        } else if (type === 'root') {
            // جذر عربي احترافي
            content = '<span style="direction:rtl; font-family:Arial;">√<span style="border-top:1px solid #000; padding-top:2px;">&nbsp;الرقم&nbsp;</span></span>&nbsp;';
        } else if (type === 'power') {
            // أس عربي
            content = '<sup>٢</sup>';
        }
        editor.insertHtml(content);
    }

    document.addEventListener('DOMContentLoaded', function() {
        CKEDITOR.on('instanceReady', function(evt) {
            var editorId = evt.editor.name;
            var container = document.getElementById(editorId).closest('.django-ckeditor-widget');
            
            var mathBar = document.createElement('div');
            mathBar.style = "margin-bottom:10px; background:#f0f7f0; padding:12px; border:2px solid #2d5a27; border-radius:10px; display:flex; align-items:center; gap:10px;";
            mathBar.innerHTML = `
                <strong style="color:#2d5a27; font-size:14px;">🧮 أدوات الرياضيات العربية:</strong>
                <button type="button" onclick="insertArabicMath('${editorId}', 'fraction')" style="cursor:pointer; background:#2d5a27; color:white; border:none; padding:6px 12px; border-radius:5px; font-weight:bold;">➕ كسر عربي</button>
                <button type="button" onclick="insertArabicMath('${editorId}', 'root')" style="cursor:pointer; background:#2d5a27; color:white; border:none; padding:6px 12px; border-radius:5px; font-weight:bold;">➕ جذر عربي</button>
                <button type="button" onclick="insertArabicMath('${editorId}', 'power')" style="cursor:pointer; background:#2d5a27; color:white; border:none; padding:6px 12px; border-radius:5px; font-weight:bold;">➕ أس²</button>
                <small style="color:#666; margin-right:auto;">(بعد الإدراج، غيري الكلمات بالأرقام العربية)</small>
            `;
            container.prepend(mathBar);
        });
    });
</script>
"""

# 3. إعداد الأسئلة داخل صفحة المهارة
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['question_text', 'choice_a', 'choice_b', 'choice_c', 'choice_d', 'correct_answer']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]

    def render_change_form(self, request, context, **kwargs):
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        # حقن المحرر الخاص في الصفحة
        new_content = response.content.decode('utf-8').replace('</body>', ARABIC_MATH_JS + '</body>')
        response.content = new_content.encode('utf-8')
        return response

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')
    
    def render_change_form(self, request, context, **kwargs):
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        new_content = response.content.decode('utf-8').replace('</body>', ARABIC_MATH_JS + '</body>')
        response.content = new_content.encode('utf-8')
        return response

# 4. تسجيل باقي الموديلات
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
