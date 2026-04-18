from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
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


@login_required
def teacher_dashboard(request):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    my_skills = TeacherSkill.objects.filter(created_by=teacher) if teacher else TeacherSkill.objects.none()
    my_exams = TeacherExam.objects.filter(skill__created_by=teacher) if teacher else TeacherExam.objects.none()
    my_results = ExamResult.objects.filter(exam__skill__created_by=teacher) if teacher else ExamResult.objects.none()
    avg_score = my_results.aggregate(avg=Avg('percentage'))['avg'] or 0
    qodrat_sessions = ClassSession.objects.filter(teacher=teacher, session_type='qodrat').count() if teacher else 0
    tahsili_sessions = ClassSession.objects.filter(teacher=teacher, session_type='tahsili').count() if teacher else 0
    context = {
        'teacher': teacher,
        'total_skills': my_skills.filter(content_type='skill').count(),
        'total_lessons': my_skills.filter(content_type='lesson').count(),
        'total_banks': my_skills.filter(content_type='bank').count(),
        'active_skills': my_skills.filter(is_active=True).count(),
        'total_exams': my_exams.count(),
        'active_exams': my_exams.filter(is_active=True).count(),
        'avg_score': round(avg_score, 1),
        'total_results': my_results.count(),
        'passed_results': my_results.filter(passed=True).count(),
        'total_students': Student.objects.count(),
        'sessions': ClassSession.objects.filter(teacher=teacher).order_by('-session_date', '-session_time')[:10] if teacher else [],
        'qodrat_sessions': qodrat_sessions,
        'tahsili_sessions': tahsili_sessions,
        'recent_skills': my_skills.order_by('-created_at')[:5],
        'weak_students': my_results.filter(passed=False).select_related('student', 'exam').order_by('percentage')[:5],
    }
    return render(request, 'teachers/dashboard.html', context)


@login_required
def skill_manager(request):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    my_skills = TeacherSkill.objects.filter(created_by=teacher).order_by('-created_at') if teacher else []
    shared_skills = TeacherSkill.objects.filter(is_shared=True, is_active=True).exclude(created_by=teacher).order_by('-created_at')[:20] if teacher else []
    context = {
        'teacher': teacher,
        'my_skills': my_skills,
        'shared_skills': shared_skills,
        'my_skills_count': my_skills.count() if teacher else 0,
    }
    return render(request, 'teachers/skill_manager.html', context)


@login_required
def add_skill(request):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    if not teacher:
        messages.error(request, 'لا يوجد حساب معلمة')
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, 'يرجى إدخال عنوان المهارة')
            return redirect('skill_manager')
        skill = TeacherSkill.objects.create(
            content_type=request.POST.get('content_type', 'skill'),
            title=title,
            skill_type=request.POST.get('skill_type', ''),
            subject=request.POST.get('subject', ''),
            description=request.POST.get('description', ''),
            created_by=teacher,
            target_classes=request.POST.get('target_classes', ''),
            is_shared=request.POST.get('is_shared') == 'on',
            is_active=request.POST.get('is_active') == 'on',
        )
        video_url = request.POST.get('video_url', '')
        plain_text = request.POST.get('plain_text', '')
        if video_url or plain_text:
            TeacherSkillContent.objects.create(skill=skill, video_url=video_url, plain_text=plain_text)
        messages.success(request, f'✅ تم إضافة "{title}" بنجاح!')
        return redirect('skill_manager')
    return render(request, 'teachers/skill_manager.html', {'teacher': teacher})


@login_required
def add_skill_complete(request):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    if not teacher:
        messages.error(request, 'لا يوجد حساب معلمة')
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        import json
        content_type = request.POST.get('content_type', 'skill')
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, 'يرجى إدخال عنوان المهارة')
            return redirect('skill_manager')
        is_active = request.POST.get('is_active') == 'on'
        skill = TeacherSkill.objects.create(
            content_type=content_type,
            title=title,
            skill_type=request.POST.get('skill_type', ''),
            subject=request.POST.get('subject', ''),
            description=request.POST.get('description', ''),
            created_by=teacher,
            target_classes=request.POST.get('target_classes', ''),
            is_shared=request.POST.get('is_shared') == 'on',
            is_active=is_active,
        )
        video_url = request.POST.get('video_url', '')
        plain_text = request.POST.get('plain_text', '')
        if video_url or plain_text:
            TeacherSkillContent.objects.create(skill=skill, video_url=video_url, plain_text=plain_text)
        if content_type == 'skill':
            pre_exam = TeacherExam.objects.create(
                skill=skill, exam_type='pre',
                questions_count=int(request.POST.get('pre_count', 10)),
                duration_minutes=int(request.POST.get('pre_time', 15)),
                pass_score=int(request.POST.get('pre_pass', 60)),
                delivery=request.POST.get('pre_delivery', 'both'),
                is_active=is_active,
            )
            try:
                pre_qs = json.loads(request.POST.get('pre_questions', '[]'))
                for i, q in enumerate(pre_qs):
                    TeacherQuestion.objects.create(
                        exam=pre_exam, order=i+1,
                        question_plain=q.get('text', ''),
                        option_a_plain=q.get('a', ''), option_b_plain=q.get('b', ''),
                        option_c_plain=q.get('c', ''), option_d_plain=q.get('d', ''),
                        correct_answer=q.get('correct', 'A'), feedback_plain=q.get('feedback', ''),
                    )
            except: pass
            post_exam = TeacherExam.objects.create(
                skill=skill, exam_type='post',
                questions_count=int(request.POST.get('post_count', 10)),
                duration_minutes=int(request.POST.get('post_time', 15)),
                pass_score=int(request.POST.get('post_pass', 70)),
                is_active=is_active,
            )
            try:
                post_qs = json.loads(request.POST.get('post_questions', '[]'))
                for i, q in enumerate(post_qs):
                    TeacherQuestion.objects.create(
                        exam=post_exam, order=i+1,
                        question_plain=q.get('text', ''),
                        option_a_plain=q.get('a', ''), option_b_plain=q.get('b', ''),
                        option_c_plain=q.get('c', ''), option_d_plain=q.get('d', ''),
                        correct_answer=q.get('correct', 'A'), feedback_plain=q.get('feedback', ''),
                    )
            except: pass
        else:
            exam = TeacherExam.objects.create(
                skill=skill,
                exam_type='lesson' if content_type == 'lesson' else 'bank',
                questions_count=int(request.POST.get('pre_count', 10)),
                duration_minutes=int(request.POST.get('pre_time', 15)),
                pass_score=int(request.POST.get('pre_pass', 60)),
                is_active=is_active,
            )
            try:
                qs = json.loads(request.POST.get('pre_questions', '[]'))
                for i, q in enumerate(qs):
                    TeacherQuestion.objects.create(
                        exam=exam, order=i+1,
                        question_plain=q.get('text', ''),
                        option_a_plain=q.get('a', ''), option_b_plain=q.get('b', ''),
                        option_c_plain=q.get('c', ''), option_d_plain=q.get('d', ''),
                        correct_answer=q.get('correct', 'A'),
                        target_skill_name=q.get('skill', ''),
                        feedback_plain=q.get('feedback', ''),
                    )
            except: pass
        messages.success(request, f'✅ تم حفظ "{title}" بنجاح!')
        return redirect('skill_manager')
    return redirect('skill_manager')


@login_required
def delete_skill(request, skill_id):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    skill = get_object_or_404(TeacherSkill, id=skill_id, created_by=teacher)
    skill.delete()
    messages.success(request, '🗑️ تم حذف المهارة')
    return redirect('skill_manager')


@login_required
def add_question(request, exam_id):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    exam = get_object_or_404(TeacherExam, id=exam_id, skill__created_by=teacher)
    if request.method == 'POST':
        order = exam.questions.count() + 1
        TeacherQuestion.objects.create(
            exam=exam, order=order,
            question_plain=request.POST.get('question_plain', '').strip(),
            option_a_plain=request.POST.get('option_a_plain', ''),
            option_b_plain=request.POST.get('option_b_plain', ''),
            option_c_plain=request.POST.get('option_c_plain', ''),
            option_d_plain=request.POST.get('option_d_plain', ''),
            correct_answer=request.POST.get('correct_answer', 'A'),
            target_skill_name=request.POST.get('target_skill_name', ''),
            feedback_plain=request.POST.get('feedback_plain', ''),
        )
        messages.success(request, '✅ تم إضافة السؤال')
        return redirect('skill_manager')
    return render(request, 'teachers/add_question.html', {'exam': exam, 'teacher': teacher})


@login_required
def import_questions_excel(request, exam_id):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    exam = get_object_or_404(TeacherExam, id=exam_id, skill__created_by=teacher)
    if request.method == 'POST' and request.FILES.get('excel_file'):
        import openpyxl
        try:
            wb = openpyxl.load_workbook(request.FILES['excel_file'])
            ws = wb.active
            count = 0
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row[0]: continue
                TeacherQuestion.objects.create(
                    exam=exam, order=exam.questions.count()+1,
                    question_plain=str(row[0]) if row[0] else '',
                    option_a_plain=str(row[1]) if row[1] else '',
                    option_b_plain=str(row[2]) if row[2] else '',
                    option_c_plain=str(row[3]) if row[3] else '',
                    option_d_plain=str(row[4]) if row[4] else '',
                    correct_answer=str(row[5]).upper() if row[5] else 'A',
                    target_skill_name=str(row[6]) if len(row)>6 and row[6] else '',
                    feedback_plain=str(row[7]) if len(row)>7 and row[7] else '',
                )
                count += 1
            messages.success(request, f'✅ تم استيراد {count} سؤال!')
        except Exception as e:
            messages.error(request, f'❌ خطأ: {str(e)}')
    return redirect('skill_manager')


@login_required
def import_skills_excel(request):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    if not teacher:
        return redirect('teacher_dashboard')
    if request.method == 'POST' and request.FILES.get('excel_file'):
        import openpyxl
        try:
            wb = openpyxl.load_workbook(request.FILES['excel_file'])
            ws = wb.active
            count = 0
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row[0]: continue
                title = str(row[1]).strip() if row[1] else ''
                if not title: continue
                TeacherSkill.objects.create(
                    content_type=str(row[0]).strip() if row[0] else 'skill',
                    title=title,
                    skill_type=str(row[2]).strip() if len(row)>2 and row[2] else '',
                    subject=str(row[3]).strip() if len(row)>3 and row[3] else '',
                    target_classes=str(row[4]).strip() if len(row)>4 and row[4] else '',
                    description=str(row[5]).strip() if len(row)>5 and row[5] else '',
                    created_by=teacher, is_active=True,
                )
                count += 1
            messages.success(request, f'✅ تم استيراد {count} مهارة!')
        except Exception as e:
            messages.error(request, f'❌ خطأ: {str(e)}')
    return redirect('skill_manager')


@login_required
def exam_results(request, exam_id):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    exam = get_object_or_404(TeacherExam, id=exam_id, skill__created_by=teacher)
    results = ExamResult.objects.filter(exam=exam).select_related('student').order_by('-percentage')
    avg = results.aggregate(avg=Avg('percentage'))['avg'] or 0
    passed = results.filter(passed=True).count()
    context = {'exam': exam, 'results': results, 'avg': round(avg,1), 'passed': passed, 'failed': results.count()-passed, 'teacher': teacher}
    return render(request, 'teachers/exam_results.html', context)


@login_required
def student_result(request, result_id):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    result = get_object_or_404(ExamResult, id=result_id, exam__skill__created_by=teacher)
    answers = StudentAnswer.objects.filter(result=result).select_related('question').order_by('question__order')
    return render(request, 'teachers/student_result.html', {'result': result, 'answers': answers, 'teacher': teacher})


@login_required
def enter_manual_score(request, result_id):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    result = get_object_or_404(ExamResult, id=result_id, exam__skill__created_by=teacher)
    if request.method == 'POST':
        score = float(request.POST.get('score', 0))
        result.score = score
        result.percentage = (score / result.total * 100) if result.total > 0 else 0
        result.passed = result.percentage >= result.exam.pass_score
        result.manually_corrected = True
        result.corrected_by = teacher
        result.save()
        messages.success(request, f'✅ تم رصد الدرجة: {score}/{result.total}')
        return redirect('student_result', result_id=result_id)
    return render(request, 'teachers/enter_score.html', {'result': result, 'teacher': teacher})


@login_required
def add_session(request):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    if request.method == 'POST':
        skill = get_object_or_404(TeacherSkill, id=request.POST.get('skill_id'))
        ClassSession.objects.create(
            teacher=teacher, skill=skill,
            session_type=request.POST.get('session_type', 'qodrat'),
            target_class=request.POST.get('target_class', ''),
            session_date=request.POST.get('session_date'),
            session_time=request.POST.get('session_time'),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, '✅ تم تسجيل الحصة')
        return redirect('teacher_dashboard')
    my_skills = TeacherSkill.objects.filter(created_by=teacher, is_active=True) if teacher else []
    return render(request, 'teachers/add_session.html', {'teacher': teacher, 'skills': my_skills})