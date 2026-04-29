from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.utils import timezone
from core.models import Profile
from students.models import Student, ClassRoom
from .models import (
    Teacher, TeacherSkill, TeacherSkillContent,
    TeacherExam, TeacherQuestion, ExamResult,
    StudentAnswer, ClassSession
)


def get_teacher(request):
    """يرجع كائن Teacher المرتبط بالمستخدم، وإن لم يوجد ينشئه تلقائياً.
    سابقاً كان يرجع None إن لم يوجد، فيفشل add_skill_complete صامتاً."""
    try:
        return Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        # auto-heal: إن دخلت معلمة (لها Profile.role==TEACHER) لكن بلا Teacher row،
        # ننشئه فوراً بدل التسبب في 500 على الحفظ.
        try:
            profile = request.user.core_profile
            if profile.role == 'TEACHER':
                full_name = (
                    f"{request.user.first_name} {request.user.last_name}".strip()
                    or request.user.username
                )
                return Teacher.objects.create(user=request.user, full_name=full_name)
        except Profile.DoesNotExist:
            pass
        return None


def check_teacher(request):
    """يفحص أن المستخدم معلمة. لا نخفي الاستثناءات الفعلية."""
    try:
        return request.user.core_profile.role == 'TEACHER'
    except Profile.DoesNotExist:
        return False


def check_teacher_or_admin(request):
    try:
        role = request.user.core_profile.role
        return role in ('TEACHER', 'ADMIN')
    except Profile.DoesNotExist:
        return False


def _safe_int(value, default, minimum=None, maximum=None):
    """تحويل آمن للأرقام يمنع crash من حقول فارغة أو نص."""
    try:
        v = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    if minimum is not None and v < minimum:
        return minimum
    if maximum is not None and v > maximum:
        return maximum
    return v


@login_required
def teacher_dashboard(request):
    """
    لوحة المعلمة الرئيسية — جميع الإحصاءات من قاعدة البيانات.

    الإصلاحات:
    - حساب excellent/mid/weak_students من ExamResult بدل البيانات المحفورة في القالب.
    - تجميع متوسط الأداء لكل طالبة (لا نتيجة فردية)، لتعطي صورة دقيقة.
    - إعادة sessions الأخيرة + المهارات الأخيرة بالقيم الحقيقية.
    """
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)
    if not teacher:
        # auto-heal: إذا لم يوجد Teacher record نُنشئه (انظر get_teacher)
        messages.warning(request, 'تم إنشاء حساب معلمة جديد لربطه ببياناتك.')
        return redirect('teacher_dashboard')

    my_skills = TeacherSkill.objects.filter(created_by=teacher)
    my_exams = TeacherExam.objects.filter(skill__created_by=teacher)
    my_results = ExamResult.objects.filter(exam__skill__created_by=teacher)

    # ─── تجميع نتائج الطالبات (متوسط أداء كل طالبة) ───────────
    # Group by student, compute avg(percentage) — يعطي صورة دقيقة للطالبة
    # بدلاً من إظهار نتيجة فردية واحدة.
    students_perf = (
        my_results
        .values('student__id', 'student__first_name', 'student__last_name', 'student__username')
        .annotate(
            avg_pct=Avg('percentage'),
            results_count=Count('id'),
            passed_count=Count('id', filter=Q(passed=True)),
        )
        .order_by('-avg_pct')
    )
    # نحوّل QuerySet إلى list مرة واحدة لتجنب تكرار الاستعلام
    students_perf = list(students_perf)

    def _name(item):
        return (
            f"{item['student__first_name']} {item['student__last_name']}".strip()
            or item['student__username']
        )

    excellent_students = [
        {'name': _name(s), 'pct': round(s['avg_pct'] or 0, 1),
         'count': s['results_count'], 'student_id': s['student__id']}
        for s in students_perf if (s['avg_pct'] or 0) >= 90
    ]
    mid_students = [
        {'name': _name(s), 'pct': round(s['avg_pct'] or 0, 1),
         'count': s['results_count'], 'student_id': s['student__id']}
        for s in students_perf if 50 <= (s['avg_pct'] or 0) < 90
    ]
    weak_students = [
        {'name': _name(s), 'pct': round(s['avg_pct'] or 0, 1),
         'count': s['results_count'], 'student_id': s['student__id']}
        for s in students_perf if (s['avg_pct'] or 0) < 50
    ]

    avg_score = my_results.aggregate(avg=Avg('percentage'))['avg'] or 0

    # ─── ترتيب أعلى 3 طالبات ──────────────────────────────────
    top_students = (excellent_students + mid_students)[:3]

    return render(request, 'teachers/dashboard.html', {
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
        'sessions': (
            ClassSession.objects
            .filter(teacher=teacher)
            .select_related('skill')
            .order_by('-session_date', '-session_time')[:10]
        ),
        'qodrat_sessions': ClassSession.objects.filter(teacher=teacher, session_type='qodrat').count(),
        'tahsili_sessions': ClassSession.objects.filter(teacher=teacher, session_type='tahsili').count(),
        'recent_skills': my_skills.order_by('-created_at')[:5],
        # تصنيف الأداء — يستعمله القالب لاستبدال البيانات الوهمية
        'excellent_students': excellent_students,
        'mid_students': mid_students,
        'weak_students': weak_students,
        'top_students': top_students,
        'students_count_excellent': len(excellent_students),
        'students_count_mid': len(mid_students),
        'students_count_weak': len(weak_students),
        'has_real_data': bool(students_perf),
    })


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
        messages.success(request, f'تم إضافة "{title}" بنجاح!')
        return redirect('skill_manager')
    return render(request, 'teachers/skill_manager.html', {'teacher': teacher})


@login_required
def add_skill_complete(request):
    """
    حفظ مهارة/درس/بنك أسئلة كاملة دفعة واحدة (wizard 5 خطوات).

    إصلاحات حرجة:
    - _safe_int بدل int() لمنع crash عند إرسال حقل فارغ.
    - bulk_create للأسئلة لتقليل INSERTs من N إلى 1.
    - رسائل خطأ واضحة بدلاً من except صامت يخفي الأخطاء.
    - log إلى console بنوع المشكلة لتسهيل التشخيص.
    """
    import json
    import logging
    logger = logging.getLogger(__name__)

    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)
    if not teacher:
        messages.error(request, 'لم يُربط حسابك بسجل معلمة. تواصلي مع المديرة.')
        return redirect('teacher_dashboard')

    if request.method != 'POST':
        return redirect('skill_manager')

    content_type = request.POST.get('content_type', 'skill')
    title = (request.POST.get('title') or '').strip()

    if not title:
        messages.error(request, 'يرجى إدخال عنوان المهارة')
        return redirect('skill_manager')

    is_active = request.POST.get('is_active') == 'on'

    # ─── إنشاء المهارة الأم ────────────────────────────────────
    try:
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
    except Exception as e:
        logger.exception('Failed to create TeacherSkill')
        messages.error(request, f'تعذّر حفظ المهارة: {e}')
        return redirect('skill_manager')

    # ─── محتوى الشرح (اختياري) ────────────────────────────────
    video_url = request.POST.get('video_url', '').strip()
    plain_text = request.POST.get('plain_text', '').strip()
    if video_url or plain_text:
        TeacherSkillContent.objects.create(
            skill=skill, video_url=video_url, plain_text=plain_text,
        )

    # ─── الاختبارات والأسئلة ──────────────────────────────────
    def _bulk_questions(exam, raw_json, key_prefix=''):
        """يحفظ قائمة أسئلة من JSON بدون فشل صامت."""
        try:
            items = json.loads(raw_json or '[]')
        except json.JSONDecodeError as exc:
            logger.warning(f'Invalid {key_prefix} questions JSON: {exc}')
            return 0
        if not isinstance(items, list):
            return 0
        objs = []
        for i, q in enumerate(items, start=1):
            if not isinstance(q, dict):
                continue
            objs.append(TeacherQuestion(
                exam=exam,
                order=i,
                question_plain=q.get('text', ''),
                option_a_plain=q.get('a', ''),
                option_b_plain=q.get('b', ''),
                option_c_plain=q.get('c', ''),
                option_d_plain=q.get('d', ''),
                correct_answer=(q.get('correct') or 'A').upper()[:1],
                target_skill_name=q.get('skill', ''),
                feedback_plain=q.get('feedback', ''),
            ))
        if objs:
            TeacherQuestion.objects.bulk_create(objs)
        return len(objs)

    pre_count = _safe_int(request.POST.get('pre_count'), default=10, minimum=1, maximum=100)
    pre_time = _safe_int(request.POST.get('pre_time'), default=15, minimum=1, maximum=300)
    pre_pass = _safe_int(request.POST.get('pre_pass'), default=60, minimum=0, maximum=100)
    post_count = _safe_int(request.POST.get('post_count'), default=10, minimum=1, maximum=100)
    post_time = _safe_int(request.POST.get('post_time'), default=15, minimum=1, maximum=300)
    post_pass = _safe_int(request.POST.get('post_pass'), default=70, minimum=0, maximum=100)

    qs_saved = 0
    if content_type == 'skill':
        # مهارة قدرات → اختباران (قبلي + بعدي)
        pre_exam = TeacherExam.objects.create(
            skill=skill, exam_type='pre',
            questions_count=pre_count, duration_minutes=pre_time,
            pass_score=pre_pass, delivery=request.POST.get('pre_delivery', 'both'),
            is_active=is_active,
        )
        qs_saved += _bulk_questions(pre_exam, request.POST.get('pre_questions'), 'pre')

        post_exam = TeacherExam.objects.create(
            skill=skill, exam_type='post',
            questions_count=post_count, duration_minutes=post_time,
            pass_score=post_pass, is_active=is_active,
        )
        qs_saved += _bulk_questions(post_exam, request.POST.get('post_questions'), 'post')
    else:
        # درس تحصيلي / بنك → اختبار واحد
        exam = TeacherExam.objects.create(
            skill=skill,
            exam_type='lesson' if content_type == 'lesson' else 'bank',
            questions_count=pre_count, duration_minutes=pre_time,
            pass_score=pre_pass, is_active=is_active,
        )
        qs_saved += _bulk_questions(exam, request.POST.get('pre_questions'), 'pre')

    if qs_saved:
        messages.success(request, f'✅ تم حفظ "{title}" بنجاح مع {qs_saved} سؤال')
    else:
        messages.success(
            request,
            f'✅ تم حفظ "{title}" — يمكنك إضافة الأسئلة لاحقاً من شاشة الأسئلة'
        )
    return redirect('skill_manager')


@login_required
def delete_skill(request, skill_id):
    if not check_teacher(request):
        return redirect('home')
    teacher = get_teacher(request)
    skill = get_object_or_404(TeacherSkill, id=skill_id, created_by=teacher)
    skill.delete()
    messages.success(request, 'تم حذف المهارة')
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
        messages.success(request, 'تم إضافة السؤال')
        return redirect('skill_manager')
    return render(request, 'teachers/add_question.html', {'exam': exam, 'teacher': teacher})


@login_required
def import_questions_excel(request, exam_id):
    try:
        is_admin = request.user.core_profile.role == 'ADMIN'
    except:
        is_admin = False

    if not is_admin and not check_teacher(request):
        return redirect('home')

    if is_admin:
        exam = get_object_or_404(TeacherExam, id=exam_id)
    else:
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
            messages.success(request, f'تم استيراد {count} سؤال!')
        except Exception as e:
            messages.error(request, f'خطأ: {str(e)}')

    if is_admin:
        return redirect('admin_comprehensive')
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
            messages.success(request, f'تم استيراد {count} مهارة!')
        except Exception as e:
            messages.error(request, f'خطأ: {str(e)}')
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
    context = {
        'exam': exam,
        'results': results,
        'avg': round(avg, 1),
        'passed': passed,
        'failed': results.count()-passed,
        'teacher': teacher,
    }
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
        messages.success(request, f'تم رصد الدرجة: {score}/{result.total}')
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
        messages.success(request, 'تم تسجيل الحصة')
        return redirect('teacher_dashboard')
    my_skills = TeacherSkill.objects.filter(created_by=teacher, is_active=True) if teacher else []
    return render(request, 'teachers/add_session.html', {'teacher': teacher, 'skills': my_skills})


@login_required
def get_skill_questions(request, skill_id):
    teacher = get_teacher(request)
    skill = get_object_or_404(TeacherSkill, id=skill_id, created_by=teacher)
    data = {'skill': skill.title, 'exams': []}
    for exam in skill.exams.all():
        exam_data = {
            'type': exam.exam_type,
            'type_label': exam.get_exam_type_display(),
            'count': exam.questions.count(),
            'time': exam.duration_minutes,
            'pass_score': exam.pass_score,
            'questions': []
        }
        for q in exam.questions.all().order_by('order'):
            exam_data['questions'].append({
                'order': q.order,
                'text': q.question_plain,
                'a': q.option_a_plain,
                'b': q.option_b_plain,
                'c': q.option_c_plain,
                'd': q.option_d_plain,
                'correct': q.correct_answer,
                'feedback': q.feedback_plain,
            })
        data['exams'].append(exam_data)
    return JsonResponse(data)
