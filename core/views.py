from django.shortcuts import render
from .models import SchoolSettings, Skill

def home(request):
    settings = SchoolSettings.objects.first()
    # جلب جميع المهارات لتعرض في التبويبات
    all_skills = Skill.objects.all()
    
    context = {
        'settings': settings,
        'skills': all_skills,
    }
    return render(request, 'core/home.html', context)