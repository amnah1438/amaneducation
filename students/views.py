"""
Students views — لوحة الطالبة + استيراد + إدارة + خوض الاختبارات.

الإصلاحات الجوهرية:
1) إزالة get_student القائم على __icontains (كان يربط طالبة بأخرى ذات اسم مشابه).
   نستبدله بربط مباشر عبر User.profile.national_id ↔ Student.national_id.
2) إضافة حقل national_id إلى موديل Student (في models.py) عبر hasattr safety.
3) منع الطالبة من إعادة الاختبار + قفل الاختبار عند انتهاء المدة.
4) annotate في manage_students لإلغاء N+1.
5) حماية رفع Excel: حد للحجم + تحقق من الامتداد.
6) دعم مسار "exam_login" المستقل برقم الهوية + PIN (نفس منطق accounts).
"""
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from core.models import Profile
from teachers.models import (
    ExamResult,
    StudentAnswer,
    TeacherExam,
)

from .models import ClassRoom, Student


# حد أقصى لحجم ملفات Excel المرفوعة (5 ميجا) — حماية من DoS عبر ملفات ضخمة.
MAX_EXCEL_SIZE = 5 * 1024 * 1024


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

def _is_student(user):
    try:
        return user.core_profile.role == 'STUDENT'
    except Profile.DoesNotExist:
        return False


def _is_admin_or_teacher(user):
    try:
        return user.core_profile.role in ('ADMIN', 'TEACHER')
    except Profile.DoesNotExist:
        return user.is_superuser


def _student_for(user):
    """
    يرجع كائن Student المرتبط بالمستخدم.
    الربط الصحيح: profile.national_id == student.national_id (إن وُجد الحقل)،
    وإلا fallback على المطابقة الكاملة بالاسم — لا __icontains الهشّ.
    """
    try:
        profile = user.core_profile
    except Profile.DoesNotExist:
        return None

    # المسار 1: ربط برقم الهوية (إن أُضيف الحقل لاحقاً)
    if hasattr(Student, 'national_id') and profile.national_id:
        s = Student.objects.filter(national_id=profile.national_id).first()
        if s:
            return s

    # المسار 2: ربط بالاسم الكامل المطابق تماماً (آمن من الالتباس)
    full_name = (f"{user.first_name} {user.last_name}").strip()
    if full_name:
        return Student.objects.filter(full_name=full_name).first()
    return None


# ═══════════════════════════════════════════════════════════════
# استيراد الطالبات
# ═══════════════════════════════════════════════════════════════

@login_required
def import_students_excel(request):
    if not _is_admin_or_teacher(request.user):
        return redirect('home')

    if request.method == 'POST':
        excel = request.FILES.get('excel_file')
        if not excel:
            messages.error(request, 'لم يُرفع ملف')
            return render(request, 'students/import_students.html')

        # حماية: حجم + امتداد
        if excel.size > MAX_EXCEL_SIZE:
            messages.error(request, 'حجم الملف يتجاوز 5 ميجا')
            return render(request, 'students/import_students.html')
        if not excel.name.lower().endswith(('.xlsx', '.xlsm')):
            messages.error(request, 'الصيغة المدعومة: xlsx/xlsm')
            return render(request, 'students/import_students.html')

        try:
            import openpyxl
            wb = openpyxl.load_workbook(excel, data_only=True)
            ws = wb.active
        except Exception as e:
            messages.error(request, f'❌ تعذّر فتح الملف: {e}')
            return render(request, 'students/import_students.html')

        count, errors = 0, []
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:
                continue
            full_name = str(row[0]).strip() if row[0] else ''
            national_id = str(row[1]).strip() if len(row) > 1 and row[1] else ''
            classroom_name = str(row[2]).strip() if len(row) > 2 and row[2] else 'ث١٢'

            if not full_name or not national_id:
                continue
            if not national_id.isdigit():
                errors.append(f'{full_name}: رقم هوية غير صالح')
                continue

            try:
                classroom, _ = ClassRoom.objects.get_or_create(name=classroom_name)
                Student.objects.get_or_create(
                    full_name=full_name,
                    defaults={'classroom': classroom},
                )
                if not User.objects.filter(username=national_id).exists():
                    parts = full_name.split()
                    user = User.objects.create_user(
                        username=national_id,
                        password=national_id,
                        first_name=parts[0] if parts else full_name,
                        last_name=' '.join(parts[1:]) if len(parts) > 1 else '',
                    )
                    Profile.objects.create(
                        user=user,
                        role='STUDENT',
                        national_id=national_id,
                    )
                    count += 1
            except Exception as e:
                errors.append(f'{full_name}: {e}')

        if errors:
            messages.warning(
                request,
                f'✅ استُورد {count} مع {len(errors)} أخطاء — ' + ' | '.join(errors[:5]),
            )
        else:
            messages.success(request, f'✅ تم استيراد {count} طالبة بنجاح!')

    return render(request, 'students/import_students.html')


# ═══════════════════════════════════════════════════════════════
# إضافة طالبة يدوياً (نموذج واحد)
# ═══════════════════════════════════════════════════════════════

@login_required
@require_POST
def add_student_manual(request):
    """
    إضافة طالبة واحدة يدوياً من صفحة الاستيراد.

    تكامل آمن:
    - تحقق من رقم الهوية (8-12 رقماً).
    - رفض التكرار.
    - إنشاء User + Profile + Student + ClassRoom دفعة واحدة.
    - رمز PIN اختياري؛ إن لم يُدخل تستعمل الطالبة رقم هويتها.
    """
    if not _is_admin_or_teacher(request.user):
        return redirect('home')

    full_name = (request.POST.get('full_name') or '').strip()
    national_id = (request.POST.get('national_id') or '').strip()
    classroom_name = (request.POST.get('classroom_name') or 'ث١٢').strip()
    pin_code = (request.POST.get('pin_code') or '').strip()

    # ─── تحقق من المدخلات ──────────────────────────────────────
    if not full_name:
        messages.error(request, 'يرجى إدخال اسم الطالبة')
        return redirect('import_students_excel')
    if not national_id.isdigit() or not (8 <= len(national_id) <= 12):
        messages.error(request, 'رقم الهوية يجب أن يكون 8-12 رقماً')
        return redirect('import_students_excel')
    if pin_code and not pin_code.isdigit():
        messages.error(request, 'رمز PIN يجب أن يكون أرقاماً فقط')
        return redirect('import_students_excel')
    if User.objects.filter(username=national_id).exists():
        messages.warning(request, f'⚠️ رقم الهوية {national_id} مسجّل مسبقاً')
        return redirect('import_students_excel')

    # ─── إنشاء البيانات ────────────────────────────────────────
    try:
        classroom, _ = ClassRoom.objects.get_or_create(name=classroom_name)
        parts = full_name.split()
        user = User.objects.create_user(
            username=national_id,
            password=national_id,  # كلمة مرور افتراضية = رقم الهوية
            first_name=parts[0] if parts else full_name,
            last_name=' '.join(parts[1:]) if len(parts) > 1 else '',
        )
        Profile.objects.create(
            user=user,
            role='STUDENT',
            national_id=national_id,
            pin_code=pin_code,  # فارغ يعني الـ fallback لكلمة المرور
        )
        Student.objects.create(full_name=full_name, classroom=classroom)
        messages.success(request, f'✅ تم إضافة الطالبة {full_name} في فصل {classroom.name}')
    except Exception as e:
        messages.error(request, f'❌ تعذّر الحفظ: {e}')

    return redirect('import_students_excel')


# ═══════════════════════════════════════════════════════════════
# داشبورد الطالبة
# ═══════════════════════════════════════════════════════════════

@login_required
def student_dashboard(request):
    if not _is_student(request.user):
        return redirect('home')

    # نحسب المتوسط في الـ DB بدل اجترار النتائج إلى Python
    stats = (
        ExamResult.objects
        .filter(student=request.user)
        .aggregate(
            total=Count('id'),
            passed=Count('id', filter=Q(passed=True)),
            avg=Avg('percentage'),
        )
    )

    my_results = (
        ExamResult.objects
        .filter(student=request.user)
        .select_related('exam', 'exam__skill')
        .order_by('-submitted_at')[:10]
    )

    done_exam_ids = ExamResult.objects.filter(
        student=request.user
    ).values_list('exam_id', flat=True)

    # اختبارات لها تعيينات محددة (علاجية) — لا تظهر للكل
    from .models import RemedialExamAssignment
    restricted_exam_ids = set(
        RemedialExamAssignment.objects.values_list('exam_id', flat=True).distinct()
    )
    # اختبارات معيّنة لهذه الطالبة تحديداً
    my_student = _student_for(request.user)
    my_assigned_ids = set(
        RemedialExamAssignment.objects.filter(student=my_student).values_list('exam_id', flat=True)
    ) if my_student else set()

    available_exams = (
        TeacherExam.objects
        .filter(is_active=True)
        .filter(
            Q(id__in=my_assigned_ids) |  # علاجية مُعيَّنة: تظهر حتى لو أُدّيت
            (~Q(id__in=restricted_exam_ids) & ~Q(id__in=done_exam_ids))  # عادية: غير مكتملة وغير محجوبة
        )
        .select_related('skill')
    )

    return render(request, 'students/dashboard.html', {
        'my_results': my_results,
        'available_exams': available_exams,
        'total_exams': stats['total'] or 0,
        'passed_exams': stats['passed'] or 0,
        'avg_score': round(stats['avg'] or 0, 1),
    })


# ═══════════════════════════════════════════════════════════════
# خوض الاختبار
# ═══════════════════════════════════════════════════════════════

@require_http_methods(["GET", "POST"])
def take_exam(request, exam_id):
    """
    خوض الاختبار:
    - إن لم تكن مسجّلة دخول → نطلب رقم الهوية + PIN ثم نسجّل دخولها كطالبة.
    - منع إعادة الاختبار: لو وُجدت نتيجة سابقة نمنعها.
    - حساب النتيجة + الانتقال للنتيجة.
    """
    exam = get_object_or_404(TeacherExam, id=exam_id, is_active=True)

    # ─── 1) دخول قبل بدء الاختبار ─────────────────────────────
    # متوافق مع نظام الدخول الموحّد. يقبل الهوية بأرقام عربية أو لاتينية.
    if not request.user.is_authenticated:
        if request.method == 'POST' and request.POST.get('national_id'):
            national_id = (request.POST.get('national_id') or '').strip()
            pin = (request.POST.get('pin_code') or '').strip()

            # تحقق متساهل (يقبل الأرقام العربية) — 10 أرقام للهوية السعودية
            from accounts.views import _is_valid_id, _id_variants
            if not _is_valid_id(national_id, exact=10):
                return render(request, 'students/exam_login.html', {
                    'exam': exam, 'error': 'رقم الهوية الوطنية يجب أن يكون 10 أرقام',
                })

            profile = Profile.objects.select_related('user').filter(
                national_id__in=_id_variants(national_id), role='STUDENT'
            ).first()
            if profile is None:
                return render(request, 'students/exam_login.html', {
                    'exam': exam, 'error': 'رقم الهوية غير موجود — تواصلي مع المعلمة',
                })

            user = profile.user
            if not user.is_active:
                return render(request, 'students/exam_login.html', {
                    'exam': exam, 'error': 'الحساب غير مفعّل',
                })

            # طالبة لها PIN → يجب التطابق
            if profile.pin_code:
                if not pin or profile.pin_code != pin:
                    return render(request, 'students/exam_login.html', {
                        'exam': exam, 'error': 'رمز التحقق غير صحيح',
                        'require_pin': True,
                    })
            # طالبة بدون PIN → الهوية وحدها كافية

            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            request.session.cycle_key()
            # نواصل التدفق العادي بعد تسجيل الدخول
        else:
            return render(request, 'students/exam_login.html', {'exam': exam})

    # ─── 2) منع إعادة الاختبار ────────────────────────────────
    if ExamResult.objects.filter(exam=exam, student=request.user).exists():
        messages.warning(request, '⚠️ لقد أدّيتِ هذا الاختبار مسبقاً')
        return redirect('student_dashboard')

    questions = list(exam.questions.all().order_by('order'))
    if not questions:
        messages.error(request, '❌ لا توجد أسئلة في هذا الاختبار')
        return redirect('student_dashboard')

    # ─── 3) تسليم الاختبار ────────────────────────────────────
    if request.method == 'POST' and request.POST.get('time_taken') is not None:
        score = 0
        total = len(questions)
        # نُنشئ النتيجة أولاً (transaction-style)
        result = ExamResult.objects.create(
            exam=exam,
            student=request.user,
            total=total,
            score=0,
            percentage=0,
            passed=False,
            time_taken_seconds=_safe_int(request.POST.get('time_taken'), 0, minimum=0),
        )
        # نخزّن إجابات الطالبة + نحسب النتيجة في تكرار واحد
        answers_to_create = []
        for q in questions:
            chosen = (request.POST.get(f'q_{q.id}') or '').strip().upper()
            is_correct = chosen == q.correct_answer
            if is_correct:
                score += 1
            answers_to_create.append(StudentAnswer(
                result=result,
                question=q,
                chosen_answer=chosen[:1],  # نضمن طول 1
                is_correct=is_correct,
            ))
        StudentAnswer.objects.bulk_create(answers_to_create)

        percentage = round((score / total * 100), 1) if total > 0 else 0
        result.score = score
        result.percentage = percentage
        result.passed = percentage >= exam.pass_score
        result.save(update_fields=['score', 'percentage', 'passed'])

        messages.success(request, f'✅ تم التسليم — نتيجتك: {score}/{total}')
        return redirect('student_result_view', result_id=result.id)

    return render(request, 'students/take_exam.html', {
        'exam': exam,
        'questions': questions,
        'duration': exam.duration_minutes * 60,
    })


def _safe_int(value, default, minimum=None):
    """نسخة خفيفة من _safe_int (مكررة هنا لتجنب coupling مع core)."""
    try:
        v = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    if minimum is not None and v < minimum:
        return minimum
    return v


# ═══════════════════════════════════════════════════════════════
# نتيجة الطالبة
# ═══════════════════════════════════════════════════════════════

@login_required
def student_result_view(request, result_id):
    if not _is_student(request.user):
        return redirect('home')

    # student=request.user → يضمن ألا ترى الطالبة نتيجة طالبة أخرى
    result = get_object_or_404(
        ExamResult.objects.select_related('exam', 'exam__skill'),
        id=result_id, student=request.user,
    )
    answers = list(
        StudentAnswer.objects
        .filter(result=result)
        .select_related('question')
        .order_by('question__order')
    )
    # نُجهّز إحصاءات إضافية للعرض
    correct = sum(1 for a in answers if a.is_correct)
    incorrect = len(answers) - correct
    duration = result.time_taken_seconds or 0
    minutes = duration // 60
    seconds = duration % 60

    # تصنيف الأداء (للرسالة المحفّزة)
    pct = float(result.percentage or 0)
    if pct >= 90:
        verdict = ('🏆', 'أداء استثنائي', 'var(--green)')
    elif pct >= 70:
        verdict = ('🌟', 'أداء جيد جداً', 'var(--blue)')
    elif pct >= 50:
        verdict = ('👍', 'أداء مقبول — يمكنكِ التحسّن', 'var(--orange)')
    else:
        verdict = ('💪', 'تحتاجين مراجعة هذه المهارة', 'var(--red)')

    print_mode = request.GET.get('print') == '1'

    from core.models import SchoolSettings
    return render(request, 'students/result.html', {
        'result': result,
        'answers': answers,
        'correct': correct,
        'incorrect': incorrect,
        'duration_min': minutes,
        'duration_sec': seconds,
        'verdict_icon': verdict[0],
        'verdict_text': verdict[1],
        'verdict_color': verdict[2],
        'print_mode': print_mode,
        'settings': SchoolSettings.objects.first(),
    })


# ═══════════════════════════════════════════════════════════════
# إدارة الطالبات (مديرة + معلمة)
# ═══════════════════════════════════════════════════════════════

@login_required
def manage_students(request):
    if not _is_admin_or_teacher(request.user):
        return redirect('home')

    # POST: حذف / تفعيل / تعطيل
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        if user_id:
            target = User.objects.filter(id=user_id).first()
            if target is None:
                messages.error(request, 'المستخدمة غير موجودة')
            elif target.is_superuser:
                messages.error(request, 'لا يمكن تعديل حساب superuser من هنا')
            elif action == 'delete':
                target.delete()
                messages.success(request, '🗑️ تم حذف الطالبة بنجاح')
            elif action == 'toggle':
                target.is_active = not target.is_active
                target.save(update_fields=['is_active'])
                status = 'تفعيل' if target.is_active else 'تعطيل'
                messages.success(request, f'✅ تم {status} حساب الطالبة')
            else:
                messages.error(request, 'إجراء غير معروف')
        return redirect('manage_students')

    # GET: استعلام واحد بـ annotate يحسب results_count و passed_count
    profiles = (
        Profile.objects
        .filter(role='STUDENT')
        .select_related('user')
        .annotate(
            results_count=Count('user__teacher_exam_results', distinct=True),
            passed_count=Count(
                'user__teacher_exam_results',
                filter=Q(user__teacher_exam_results__passed=True),
                distinct=True,
            ),
        )
        .order_by('user__first_name')
    )

    # نجلب كل الطلاب مرة واحدة بدل استعلام لكل طالبة (إن أمكن)
    student_index = {}
    for s in Student.objects.select_related('classroom').all():
        student_index.setdefault(s.full_name, s)

    students_data = []
    for p in profiles:
        full_name = (f"{p.user.first_name} {p.user.last_name}".strip()
                     or p.user.username)
        student = student_index.get(full_name)
        students_data.append({
            'profile': p,
            'user': p.user,
            'student': student,
            'classroom': student.classroom.name if student and student.classroom else '—',
            'full_name': full_name,
            'national_id': p.national_id,
            'is_active': p.user.is_active,
            'last_login': p.user.last_login,
            'results_count': p.results_count,
            'passed_count': p.passed_count,
        })

    return render(request, 'students/manage_students.html', {
        'students_data': students_data,
        'total': len(students_data),
        # نحسب الإحصاءات في view (بدلاً من حلقات template الهشة)
        'active_count': sum(1 for s in students_data if s['is_active']),
        'inactive_count': sum(1 for s in students_data if not s['is_active']),
    })
