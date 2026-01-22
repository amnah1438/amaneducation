from django.shortcuts import render, get_object_or_404
from .models import SchoolSettings, Skill

# --- دالة الصفحة الرئيسية ---
def home(request):
    settings = SchoolSettings.objects.first()
    all_skills = Skill.objects.all()
    
    context = {
        'settings': settings,
        'skills': all_skills,
    }
    return render(request, 'core/home.html', context)

# --- دالة تفاصيل المهارة (صفحة الفيديو والوصف) ---
def skill_detail(request, skill_id):
    settings = SchoolSettings.objects.first()
    skill = get_object_or_404(Skill, pk=skill_id)
    
    context = {
        'settings': settings,
        'skill': skill,
    }
    return render(request, 'skill_detail.html', context)

# --- الدالة الجديدة: دالة صفحة الاختبار (هذا ما أضفته لكِ) ---
def take_test(request, skill_id):
    settings = SchoolSettings.objects.first()
    skill = get_object_or_404(Skill, pk=skill_id)
    
    # جلب الأسئلة القبلية (PRE) المحددة لهذه المهارة
    questions = skill.questions.filter(test_type='PRE')
    
    context = {
        'settings': settings,
        'skill': skill,
        'questions': questions,
    }
    return render(request, 'core/take_test.html', context)
