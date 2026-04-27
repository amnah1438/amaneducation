from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import SchoolSettings
from teachers.models import (
    TeacherSkill, TeacherExam, ExamResult, ClassSession
)
from students.models import ClassRoom


def home(request):
    settings_obj = SchoolSettings.objects.first()

    qodrat_kamy = TeacherSkill.objects.filter(
        is_active=True, skill_type='كمي'
    ).order_by('-created_at')

    qodrat_lafzy = TeacherSkill.objects.filter(
        is_active=True, skill_type='لفظي'
    ).order_by('-created_at')

    tahsili = TeacherSkill.objects.filter(
        is_active=True, content_type='lesson'
    ).order_by('-created_at')

    banks = TeacherSkill.objects.filter(
        is_active=True, content_type='bank'
    ).order_by('-created_at')

    all_skills = TeacherSkill.objects.filter(is_active=True).order_by('-created_at')

    context = {
        'settings': settings_obj,
        'skills': all_skills,
        'qodrat_kamy': qodrat_kamy,
        'qodrat_lafzy': qodrat_lafzy,
        'tahsili': tahsili,
        'banks': banks,
        'classrooms': ClassRoom.objects.all(),
    }
    return render(request, 'core/home.html', context)def skill_detail(request, skill_id):
    settings_obj = SchoolSettings.objects.first()
    skill = get_object_or_404(TeacherSkill, pk=skill_id)
    exams = skill.exams.all()
    pre_exam = exams.filter(exam_type='pre').first()
    post_exam = exams.filter(exam_type='post').first()
    classrooms = ClassRoom.objects.all()

    context = {
        'settings': settings_obj,
        'skill': skill,
        'pre_exam': pre_exam,
        'post_exam': post_exam,
        'classrooms': classrooms,
    }
    return render(request, 'core/skill_detail.html', context)


@login_required
def activate_exam(request, exam_id):
    """تفعيل اختبار لفصل معين وإرجاع الرابط"""
    exam = get_object_or_404(TeacherExam, pk=exam_id)

    if request.method == 'POST':
        classroom_id = request.POST.get('classroom_id')
        classroom = get_object_or_404(ClassRoom, pk=classroom_id)

        # تفعيل الاختبار
        exam.is_active = True
        exam.save()

        # تسجيل الحصة تلقائياً
        try:
            from teachers.models import Teacher
            teacher = Teacher.objects.get(user=request.user)
            ClassSession.objects.get_or_create(
                teacher=teacher,
                skill=exam.skill,
                session_type='qodrat' if exam.skill.skill_type in ['كمي', 'لفظي'] else 'tahsili',
                target_class=classroom.name,
                session_date=timezone.now().date(),
                defaults={
                    'session_time': timezone.now().time(),
                    'notes': f'تفعيل تلقائي — {exam.get_exam_type_display()}',
                }
            )
        except:
            pass

        # رابط الاختبار
        exam_url = request.build_absolute_uri(
            f'/students/exam/{exam.id}/'
        )

        return JsonResponse({
            'success': True,
            'url': exam_url,
            'message': f'✅ تم تفعيل {exam.get_exam_type_display()} للفصل {classroom.name}',
        })

    return JsonResponse({'success': False})


@login_required
def deactivate_exam(request, exam_id):
    """إيقاف تفعيل اختبار"""
    exam = get_object_or_404(TeacherExam, pk=exam_id)
    exam.is_active = False
    exam.save()
    return JsonResponse({'success': True})
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
                teacher=teacher,
                skill=exam.skill,
                session_type='qodrat' if exam.skill.skill_type in ['كمي','لفظي'] else 'tahsili',
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