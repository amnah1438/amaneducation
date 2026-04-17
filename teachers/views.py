from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.http import JsonResponse
from core.models import Profile
from students.models import Student, ClassRoom
from .models import (
    Teacher, TeacherSkill, TeacherSkillContent,
    TeacherExam, TeacherQuestion, ExamResult,
    StudentAnswer, ClassSession
)


def get_teacher(request):
    try:
        return Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return None


def check_teacher(request):
    try:
        profile = request.user.core_profile
        if profile.role != 'TEACHER':
            return False
        return True
    except:
        return False


# ═══════════════════════════════════════
# داشبورد المعلمة
# ═══════════════════════════════════════

@login_required
def teacher_dashboard(request):
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)

    my_skills = TeacherSkill.objects.filter(
        created_by=teacher
    ) if teacher else TeacherSkill.objects.none()

    total_skills = my_skills.filter(content_type='skill').count()
    total_lessons = my_skills.filter(content_type='lesson').count()
    total_banks = my_skills.filter(content_type='bank').count()
    active_skills = my_skills.filter(is_active=True).count()

    my_exams = TeacherExam.objects.filter(
        skill__created_by=teacher
    ) if teacher else TeacherExam.objects.none()

    total_exams = my_exams.count()
    active_exams = my_exams.filter(is_active=True).count()

    my_results = ExamResult.objects.filter(
        exam__skill__created_by=teacher
    ) if teacher else ExamResult.objects.none()

    avg_score = my_results.aggregate(avg=Avg('percentage'))['avg'] or 0
    total_results = my_results.count()
    passed_results = my_results.filter(passed=True).count()

    total_students = Student.objects.count()

    sessions = ClassSession.objects.filter(
        teacher=teacher
    ).select_related('skill', 'exam').order_by('-session_date', '-session_time')[:10] if teacher else []

    qodrat_sessions = ClassSession.objects.filter(
        teacher=teacher, session_type='qodrat'
    ).count() if teacher else 0

    tahsili_sessions = ClassSession.objects.filter(
        teacher=teacher, session_type='tahsili'
    ).count() if teacher else 0

    recent_skills = my_skills.order_by('-created_at')[:5]

    weak_students = my_results.filter(
        passed=False
    ).select_related('student', 'exam').order_by('percentage')[:5]

    context = {
        'teacher': teacher,
        'total_skills': total_skills,
        'total_lessons': total_lessons,
        'total_banks': total_banks,
        'active_skills': active_skills,
        'total_exams': total_exams,
        'active_exams': active_exams,
        'avg_score': round(avg_score, 1),
        'total_results': total_results,
        'passed_results': passed_results,
        'total_students': total_students,
        'sessions': sessions,
        'qodrat_sessions': qodrat_sessions,
        'tahsili_sessions': tahsili_sessions,
        'recent_skills': recent_skills,
        'weak_students': weak_students,
    }

    return render(request, 'teachers/dashboard.html', context)


# ═══════════════════════════════════════
# إدارة المهارات
# ═══════════════════════════════════════

@login_required
def skill_manager(request):
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)

    my_skills = TeacherSkill.objects.filter(
        created_by=teacher
    ).order_by('-created_at') if teacher else []

    shared_skills = TeacherSkill.objects.filter(
        is_shared=True, is_active=True
    ).exclude(
        created_by=teacher
    ).order_by('-created_at')[:20] if teacher else []

    context = {
        'teacher': teacher,
        'my_skills': my_skills,
        'shared_skills': shared_skills,
        'my_skills_count': len(my_skills) if isinstance(my_skills, list) else my_skills.count(),
    }

    return render(request, 'teachers/skill_manager.html', context)


@login_required
def add_skill(request):
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)

    if not teacher:
        messages.error(request, 'لا يوجد حساب معلمة مرتبط بهذا المستخدم')
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        content_type = request.POST.get('content_type', 'skill')
        title = request.POST.get('title', '').strip()
        skill_type = request.POST.get('skill_type', '')
        subject = request.POST.get('subject', '')
        description = request.POST.get('description', '')
        target_classes = request.POST.get('target_classes', '')
        is_shared = request.POST.get('is_shared') == 'on'
        is_active = request.POST.get('is_active') == 'on'

        if not title:
            messages.error(request, 'يرجى إدخال عنوان المهارة')
            return redirect('add_skill')

        skill = TeacherSkill.objects.create(
            content_type=content_type,
            title=title,
            skill_type=skill_type,
            subject=subject,
            description=description,
            created_by=teacher,
            target_classes=target_classes,
            is_shared=is_shared,
            is_active=is_active,
        )

        video_url = request.POST.get('video_url', '')
        plain_text = request.POST.get('plain_text', '')

        if video_url or plain_text:
            TeacherSkillContent.objects.create(
                skill=skill,
                video_url=video_url,
                plain_text=plain_text,
            )

        messages.success(request, f'✅ تم إضافة "{title}" بنجاح!')
        return redirect('skill_manager')

    return render(request, 'teachers/add_skill.html', {'teacher': teacher})


@login_required
def delete_skill(request, skill_id):
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)
    skill = get_object_or_404(TeacherSkill, id=skill_id, created_by=teacher)
    skill.delete()
    messages.success(request, '🗑️ تم حذف المهارة')
    return redirect('skill_manager')


# ═══════════════════════════════════════
# إدارة الأسئلة
# ═══════════════════════════════════════

@login_required
def add_question(request, exam_id):
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)
    exam = get_object_or_404(TeacherExam, id=exam_id, skill__created_by=teacher)

    if request.method == 'POST':
        question_plain = request.POST.get('question_plain', '').strip()
        option_a_plain = request.POST.get('option_a_plain', '')
        option_b_plain = request.POST.get('option_b_plain', '')
        option_c_plain = request.POST.get('option_c_plain', '')
        option_d_plain = request.POST.get('option_d_plain', '')
        correct_answer = request.POST.get('correct_answer', 'A')
        target_skill_name = request.POST.get('target_skill_name', '')
        feedback_plain = request.POST.get('feedback_plain', '')

        order = exam.questions.count() + 1

        TeacherQuestion.objects.create(
            exam=exam,
            order=order,
            question_plain=question_plain,
            option_a_plain=option_a_plain,
            option_b_plain=option_b_plain,
            option_c_plain=option_c_plain,
            option_d_plain=option_d_plain,
            correct_answer=correct_answer,
            target_skill_name=target_skill_name,
            feedback_plain=feedback_plain,
        )

        messages.success(request, '✅ تم إضافة السؤال')
        return redirect('skill_manager')

    context = {'exam': exam, 'teacher': teacher}
    return render(request, 'teachers/add_question.html', context)


# ═══════════════════════════════════════
# استيراد من Excel
# ═══════════════════════════════════════

@login_required
def import_questions_excel(request, exam_id):
    """استيراد أسئلة من Excel"""
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)
    exam = get_object_or_404(TeacherExam, id=exam_id, skill__created_by=teacher)

    if request.method == 'POST' and request.FILES.get('excel_file'):
        import openpyxl
        excel_file = request.FILES['excel_file']

        try:
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active
            count = 0

            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row[0]:
                    continue

                question_plain = str(row[0]) if row[0] else ''
                option_a = str(row[1]) if row[1] else ''
                option_b = str(row[2]) if row[2] else ''
                option_c = str(row[3]) if row[3] else ''
                option_d = str(row[4]) if row[4] else ''
                correct = str(row[5]).upper() if row[5] else 'A'
                skill_name = str(row[6]) if len(row) > 6 and row[6] else ''
                feedback = str(row[7]) if len(row) > 7 and row[7] else ''

                order = exam.questions.count() + 1

                TeacherQuestion.objects.create(
                    exam=exam,
                    order=order,
                    question_plain=question_plain,
                    option_a_plain=option_a,
                    option_b_plain=option_b,
                    option_c_plain=option_c,
                    option_d_plain=option_d,
                    correct_answer=correct,
                    target_skill_name=skill_name,
                    feedback_plain=feedback,
                )
                count += 1

            messages.success(request, f'✅ تم استيراد {count} سؤال بنجاح!')

        except Exception as e:
            messages.error(request, f'❌ خطأ في الملف: {str(e)}')

    return redirect('skill_manager')


@login_required
def import_skills_excel(request):
    """استيراد مهارات ودروس من Excel"""
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)

    if not teacher:
        messages.error(request, 'لا يوجد حساب معلمة')
        return redirect('teacher_dashboard')

    if request.method == 'POST' and request.FILES.get('excel_file'):
        import openpyxl
        excel_file = request.FILES['excel_file']

        try:
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active
            count = 0

            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row[0]:
                    continue

                content_type = str(row[0]).strip() if row[0] else 'skill'
                title = str(row[1]).strip() if row[1] else ''
                skill_type = str(row[2]).strip() if len(row) > 2 and row[2] else ''
                subject = str(row[3]).strip() if len(row) > 3 and row[3] else ''
                target_classes = str(row[4]).strip() if len(row) > 4 and row[4] else ''
                description = str(row[5]).strip() if len(row) > 5 and row[5] else ''

                if not title:
                    continue

                TeacherSkill.objects.create(
                    content_type=content_type,
                    title=title,
                    skill_type=skill_type,
                    subject=subject,
                    target_classes=target_classes,
                    description=description,
                    created_by=teacher,
                    is_active=True,
                )
                count += 1

            messages.success(request, f'✅ تم استيراد {count} مهارة/درس بنجاح!')

        except Exception as e:
            messages.error(request, f'❌ خطأ في الملف: {str(e)}')

    return redirect('skill_manager')


# ═══════════════════════════════════════
# النتائج والتقارير
# ═══════════════════════════════════════

@login_required
def exam_results(request, exam_id):
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)
    exam = get_object_or_404(TeacherExam, id=exam_id, skill__created_by=teacher)
    results = ExamResult.objects.filter(
        exam=exam
    ).select_related('student').order_by('-percentage')

    avg = results.aggregate(avg=Avg('percentage'))['avg'] or 0
    passed = results.filter(passed=True).count()

    context = {
        'exam': exam,
        'results': results,
        'avg': round(avg, 1),
        'passed': passed,
        'failed': results.count() - passed,
        'teacher': teacher,
    }
    return render(request, 'teachers/exam_results.html', context)


@login_required
def student_result(request, result_id):
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)
    result = get_object_or_404(
        ExamResult, id=result_id,
        exam__skill__created_by=teacher
    )
    answers = StudentAnswer.objects.filter(
        result=result
    ).select_related('question').order_by('question__order')

    context = {
        'result': result,
        'answers': answers,
        'teacher': teacher,
    }
    return render(request, 'teachers/student_result.html', context)


@login_required
def enter_manual_score(request, result_id):
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)
    result = get_object_or_404(
        ExamResult, id=result_id,
        exam__skill__created_by=teacher
    )

    if request.method == 'POST':
        score = float(request.POST.get('score', 0))
        total = result.total
        result.score = score
        result.percentage = (score / total * 100) if total > 0 else 0
        result.passed = result.percentage >= result.exam.pass_score
        result.manually_corrected = True
        result.corrected_by = teacher
        result.save()
        messages.success(request, f'✅ تم رصد الدرجة: {score}/{total}')
        return redirect('student_result', result_id=result_id)

    return render(request, 'teachers/enter_score.html', {
        'result': result, 'teacher': teacher
    })


# ═══════════════════════════════════════
# سجل الحصص
# ═══════════════════════════════════════

@login_required
def add_session(request):
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)

    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        session_type = request.POST.get('session_type', 'qodrat')
        target_class = request.POST.get('target_class', '')
        session_date = request.POST.get('session_date')
        session_time = request.POST.get('session_time')
        notes = request.POST.get('notes', '')

        skill = get_object_or_404(TeacherSkill, id=skill_id)

        ClassSession.objects.create(
            teacher=teacher,
            skill=skill,
            session_type=session_type,
            target_class=target_class,
            session_date=session_date,
            session_time=session_time,
            notes=notes,
        )

        messages.success(request, '✅ تم تسجيل الحصة بنجاح')
        return redirect('teacher_dashboard')

    my_skills = TeacherSkill.objects.filter(
        created_by=teacher, is_active=True
    ) if teacher else []

    return render(request, 'teachers/add_session.html', {
        'teacher': teacher,
        'skills': my_skills,
    })