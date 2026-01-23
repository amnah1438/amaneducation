from django.contrib import admin
from .models import SchoolSettings, Profile, Teacher, Skill, Question

# 1. تخصيص عنوان لوحة التحكم
admin.site.site_header = "إدارة منصة آمنة التعليمية 📚"

# 2. محرر آمنة للرياضيات العربية (حل مشكلة الرموز والخيارات)
FIX_JS = """
<script>
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof CKEDITOR !== 'undefined') {
            CKEDITOR.on('instanceReady', function(ev) {
                // إجبار المحرر على الكتابة العربية الصحيحة ومنع الرموز الغريبة
                ev.editor.config.contentsLangDirection = 'rtl';
                ev.editor.config.entities = false; 
                ev.editor.config.basicEntities = false;
                ev.editor.editable().setStyle('font-family', 'Arial, sans-serif');
            });
        }
    });

    function insertArabicMath(editorId, type) {
        var editor = CKEDITOR.instances[editorId];
        var html = "";
        if (type === 'frac') {
            html = '<span style="display:inline-block; vertical-align:middle; text-align:center; direction:rtl;">' +
                   '<div style="border-bottom:1px solid #000; padding:0 5px;">بسط</div>' +
                   '<div>مقام</div></span>&nbsp;';
        } else if (type === 'sqrt') {
            html = '<span style="direction:rtl;">√<span style="border-top:1px solid #000;">&nbsp;رقم&nbsp;</span></span>&nbsp;';
        } else if (type === 'pow') {
            html = '<sup>٢</sup>';
        }
        editor.insertHtml(html);
    }
</script>
<style>
    .math-tool-bar { margin-bottom:10px; background:#e8f5e9; padding:10px; border:2px solid #2d5a27; border-radius:8px; display:flex; gap:10px; align-items:center; }
    .math-btn { cursor:pointer; background:#2d5a27; color:white; border:none; padding:5px 12px; border-radius:4px; font-weight:bold; }
</style>
"""

# 3. إعداد الأسئلة (Inline) لتظهر فيها الخيارات
class QuestionInline(admin.StackedInline): # Stacked تظهر الخيارات بشكل عمودي وواضح
    model = Question
    extra = 1
    # لم نحدد fields لكي يظهر Django كل شيء موجود في قاعدة البيانات تلقائياً

# 4. تسجيل المهارات (Skill) مرة واحدة فقط
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    inlines = [QuestionInline]

    def render_change_form(self, request, context, **kwargs):
        response = super().render_change_form(request, context, **kwargs)
        response.render()
        # إضافة أزرار الرياضيات فوق كل صندوق نص
        content = response.content.decode('utf-8')
        # كود لإضافة الأزرار برمجياً فوق الـ CKEditor
        math_buttons = """
        <script>
            CKEDITOR.on('instanceReady', function(evt) {
                var id = evt.editor.name;
                var el = document.getElementById(id).closest('.django-ckeditor-widget');
                if(el && !el.querySelector('.math-tool-bar')) {
                    var bar = document.createElement('div');
                    bar.className = 'math-tool-bar';
                    bar.innerHTML = '<strong>🧮 أدوات الرياضيات:</strong>' +
                        '<button type="button" class="math-btn" onclick="insertArabicMath(\\''+id+'\\', \\'frac\\')">كسر عربي</button>' +
                        '<button type="button" class="math-btn" onclick="insertArabicMath(\\''+id+'\\', \\'sqrt\\')">جذر عربي</button>' +
                        '<button type="button" class="math-btn" onclick="insertArabicMath(\\''+id+'\\', \\'pow\\')">أس²</button>';
                    el.prepend(bar);
                }
            });
        </script>
        """
        new_content = content.replace('</body>', FIX_JS + math_buttons + '</body>')
        response.content = new_content.encode('utf-8')
        return response

# 5. تسجيل الأسئلة بشكل منفصل أيضاً
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'skill')

# 6. تسجيل باقي الأقسام (تأكدي أنها مسجلة مرة واحدة فقط)
admin.site.register(SchoolSettings)
admin.site.register(Teacher)
admin.site.register(Profile)
