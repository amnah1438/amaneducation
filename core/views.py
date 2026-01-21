
from django.shortcuts import render, get_object_or_404
from .models import SchoolSettings, Skill

# --- دالة الصفحة الرئيسية (شغلك السابق كما هو) ---
def home(request):
    settings = SchoolSettings.objects.first()
    # جلب جميع المهارات لتعرض في التبويبات
    all_skills = Skill.objects.all()
    
    context = {
        'settings': settings,
        'skills': all_skills,
    }
    return render(request, 'core/home.html', context)

# --- الدالة الجديدة: لعرض تفاصيل المهارة/الدرس والأسئلة ---
def skill_detail(request, skill_id):
    # جلب إعدادات المنصة (للمحافظة على الشعار والألوان في كل الصفحات)
    settings = SchoolSettings.objects.first()
    
    # جلب المهارة المحددة بناءً على رقمها
    skill = get_object_or_404(Skill, pk=skill_id)
    
    # جلب الأسئلة المرتبطة بهذه المهارة
    # (لاحظي أننا لا نعرضها كلها الآن، فقط نجهزها للمرحلة القادمة)
    pre_questions = skill.questions.filter(test_type='PRE')
    post_questions = skill.questions.filter(test_type='POST')

    context = {
        'settings': settings,
        'skill': skill,
        'pre_questions': pre_questions,
        'post_questions': post_questions,
    }
    return render(request, 'core/skill_detail.html', context)
