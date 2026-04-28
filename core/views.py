from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg
from .models import SchoolSettings, Profile
from teachers.models import TeacherSkill, TeacherExam, ExamResult, ClassSession
from students.models import ClassRoom


def home(request):
    settings_obj = SchoolSettings.objects.first()
    all_skills = TeacherSkill.objects.filter(is_active=True).order_by('-created_at')
    context = {
        'settings': settings_obj,
        'skills': all_skills,
        'classrooms': ClassRoom.objects.all(),
    }
    return render(request, 'core/home.html', context)


def skill_detail(request, skill_id):
    skill = get_object_or_404(TeacherSkill, pk=skill_id)
    exams = skill.exams.all()
    context = {
        'skill': skill,
        'pre_exam': exams.filter(exam_type='pre').first(),
        'post_exam': exams.filter(exam_type='post').first(),
        'classrooms': ClassRoom.objects.all(),
    }
    return render(request, 'core/skill_detail.html', context)


def take_test(request, skill_id):
    skill = get_object_or_404(TeacherSkill, pk=skill_id)
    pre_exam = skill.exams.filter(exam_type='pre').first()
    questions = pre_exam.questions.all() if pre_exam else []
    return render(request, 'core/take_test.html', {'skill': skill, 'questions': questions})


@login_required
def activate_exam(request, exam_id):
    exam = get_object_or_404(TeacherExam, pk=exam_id)
    if request.method == 'POST':
        classroom_id = request.POST.get('classroom_id')
        classroom = get_object_or_404(ClassRoom, pk=classroom_id)
        exam.is_active = True
        exam.save()
        try:
            from teachers.models import Teacher
            teacher = Teacher.objects.get(user=request.user)
            ClassSession.objects.get_or_create(
                teacher=teacher, skill=exam.skill,
                session_type='qodrat' if exam.skill.skill_type in ['qodrat_kamy','qodrat_lafzy'] else 'tahsili',
                target_class=classroom.name,
                session_date=timezone.now().date(),
                defaults={'session_time': timezone.now().time()}
            )
        except: pass
        url = request.build_absolute_uri(f'/students/exam/{exam.id}/')
        return JsonResponse({'success': True, 'url': url, 'message': f'✅ تم تفعيل {exam.get_exam_type_display()} للفصل {classroom.name}'})
    return JsonResponse({'success': False})


@login_required
def deactivate_exam(request, exam_id):
    exam = get_object_or_404(TeacherExam, pk=exam_id)
    exam.is_active = False
    exam.save()
    return JsonResponse({'success': True})


@login_required
def admin_dashboard(request):
    try:
        if request.user.core_profile.role != 'ADMIN':
            return redirect('home')
    except:
        return redirect('home')

    from teachers.models import Teacher

    teachers_data = []
    for profile in Profile.objects.filter(role='TEACHER').select_related('user'):
        try:
            teacher = Teacher.objects.get(user=profile.user)
            skills_count = TeacherSkill.objects.filter(created_by=teacher).count()
            sessions_count = ClassSession.objects.filter(teacher=teacher).count()
            avg = ExamResult.objects.filter(
                exam__skill__created_by=teacher
            ).aggregate(avg=Avg('percentage'))['avg'] or 0
        except:
            skills_count = sessions_count = avg = 0
        teachers_data.append({
            'profile': profile,
            'user': profile.user,
            'name': f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.username,
            'national_id': profile.national_id,
            'skills_count': skills_count,
            'sessions_count': sessions_count,
            'avg_score': round(avg, 1),
            'last_login': profile.user.last_login,
        })

    students_data = []
    for profile in Profile.objects.filter(role='STUDENT').select_related('user'):
        results = ExamResult.objects.filter(student=profile.user)
        avg = results.aggregate(avg=Avg('percentage'))['avg'] or 0
        students_data.append({
            'profile': profile,
            'user': profile.user,
            'name': f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.username,
            'national_id': profile.national_id,
            'results_count': results.count(),
            'avg_score': round(avg, 1),
            'last_login': profile.user.last_login,
        })

    context = {
        'total_teachers': Profile.objects.filter(role='TEACHER').count(),
        'total_students': Profile.objects.filter(role='STUDENT').count(),
        'total_skills': TeacherSkill.objects.filter(is_active=True).count(),
        'total_results': ExamResult.objects.count(),
        'teachers_data': teachers_data,
        'students_data': students_data,
        'classrooms': ClassRoom.objects.all(),
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required
def admin_add_teacher(request):
    try:
        if request.user.core_profile.role != 'ADMIN':
            return redirect('home')
    except:
        return redirect('home')

    if request.method == 'POST':
        from django.contrib.auth.models import User
        from teachers.models import Teacher
        full_name = request.POST.get('full_name', '').strip()
        national_id = request.POST.get('national_id', '').strip()
        if not full_name or not national_id:
            messages.error(request, 'يرجى إدخال الاسم ورقم الهوية')
            return redirect('admin_dashboard')
        if User.objects.filter(username=national_id).exists():
            messages.error(request, 'رقم الهوية مسجّل مسبقاً')
            return redirect('admin_dashboard')
        name_parts = full_name.split()
        user = User.objects.create_user(
            username=national_id, password=national_id,
            first_name=name_parts[0] if name_parts else full_name,
            last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
        )
        Profile.objects.create(user=user, role='TEACHER', national_id=national_id)
        Teacher.objects.create(user=user, full_name=full_name)
        messages.success(request, f'✅ تم إضافة المعلمة {full_name}')
    return redirect('admin_dashboard')


@login_required
def admin_add_student(request):
    try:
        if request.user.core_profile.role != 'ADMIN':
            return redirect('home')
    except:
        return redirect('home')

    if request.method == 'POST':
        from django.contrib.auth.models import User
        from students.models import Student
        full_name = request.POST.get('full_name', '').strip()
        national_id = request.POST.get('national_id', '').strip()
        classroom_id = request.POST.get('classroom_id', '')
        if not full_name or not national_id:
            messages.error(request, 'يرجى إدخال الاسم ورقم الهوية')
            return redirect('admin_dashboard')
        if User.objects.filter(username=national_id).exists():
            messages.error(request, 'رقم الهوية مسجّل مسبقاً')
            return redirect('admin_dashboard')
        name_parts = full_name.split()
        user = User.objects.create_user(
            username=national_id, password=national_id,
            first_name=name_parts[0] if name_parts else full_name,
            last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
        )
        Profile.objects.create(user=user, role='STUDENT', national_id=national_id)
        classroom = ClassRoom.objects.filter(id=classroom_id).first()
        if classroom:
            Student.objects.create(full_name=full_name, classroom=classroom)
        messages.success(request, f'✅ تم إضافة الطالبة {full_name}')
    return redirect('admin_dashboard')


@login_required
def admin_delete_user(request, user_id):
    try:
        if request.user.core_profile.role != 'ADMIN':
            return redirect('home')
    except:
        return redirect('home')

    from django.contrib.auth.models import User
    try:
        user = User.objects.get(id=user_id)
        name = user.get_full_name() or user.username
        user.delete()
        messages.success(request, f'🗑️ تم حذف {name}')
    except:
        messages.error(request, 'حدث خطأ')
    return redirect('admin_dashboard')