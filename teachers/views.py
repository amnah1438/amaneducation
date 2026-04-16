from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from core.models import Profile, Skill
from students.models import Student, ClassRoom


@login_required
def teacher_dashboard(request):
    """داشبورد المعلمة"""
    
    # التأكد إن المستخدم معلمة
    try:
        profile = request.user.core_profile
        if profile.role != 'TEACHER':
            from django.shortcuts import redirect
            return redirect('home')
    except:
        from django.shortcuts import redirect
        return redirect('home')

    # --- إحصاءات سريعة ---
    total_students = Student.objects.count()
    total_skills = Skill.objects.count()
    total_classrooms = ClassRoom.objects.count()

    # --- قائمة الطالبات ---
    students = Student.objects.select_related('classroom').all()

    # --- المهارات ---
    skills = Skill.objects.all()

    context = {
        'total_students': total_students,
        'total_skills': total_skills,
        'total_classrooms': total_classrooms,
        'total_assessments': 0,
        'avg_score': 0,
        'students': students,
        'skills': skills,
    }

    return render(request, 'teachers/dashboard.html', context)