"""
Core views — الواجهة الأمامية + لوحة المديرة.

التغييرات الرئيسية في هذه النسخة:
- صلاحيات الطالبة: لا تظهر لها بنوك الأسئلة ولا اختبارات التحصيلي ولا
  الاختبار القبلي/البعدي. تظهر لها فقط: مهارات قدرات + دروس تحصيلي
  + الاختبارات الشاملة المفعّلة.
- تفعيل اختبار شامل لـ "جميع الفصول" (classroom_id == 'all').
- مسارات طباعة منفصلة للمحتوى والاختبارات (skill_print, exam_print).
- مسارات استيراد Excel للمعلمات وللطالبات من لوحة المديرة.
- تعديل/حذف الاختبارات الشاملة.
- تعديل بيانات مستخدم (تحديث الاسم/تغيير PIN).
- رسائل خطأ وتنبيهات واضحة في كل مسار.
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.models import Profile, SchoolSettings
from students.models import ClassRoom, Student
from teachers.models import (
    ClassSession,
    ExamResult,
    Teacher,
    TeacherExam,
    TeacherQuestion,
    TeacherSkill,
)


# ═══════════════════════════════════════════════════════════════
# Decorators وأدوات صلاحيات
# ═══════════════════════════════════════════════════════════════

def _get_role(user):
    """يرجع دور المستخدم (ADMIN/TEACHER/STUDENT) أو None."""
    if not user.is_authenticated:
        return None
    try:
        return user.core_profile.role
    except Profile.DoesNotExist:
        return None


def admin_required(view_func):
    """يضمن أن المستخدم مسجل دخول ودوره ADMIN (أو superuser)."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.is_superuser or _get_role(request.user) == 'ADMIN':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'هذه الصفحة مخصصة للإدارة فقط.')
        return redirect('home')
    return _wrapped


def _safe_int(value, default, minimum=None, maximum=None):
    """تحويل آمن للأعداد مع حدود اختيارية — لا يطرح ValueError."""
    try:
        result = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    if minimum is not None and result < minimum:
        return minimum
    if maximum is not None and result > maximum:
        return maximum
    return result


# ═══════════════════════════════════════════════════════════════
# الصفحات العامة + صلاحيات المحتوى للطالبة
# ═══════════════════════════════════════════════════════════════

# أنواع المحتوى التي يحق للطالبة رؤيتها في الصفحة الرئيسية:
#   - skill        : مهارة قدرات (تحوي محتوى + قبلي/بعدي، لكنها تُعرض هنا
#                    كبطاقة محتوى. فلترة الاختبار القبلي/البعدي تتم في
#                    skill_detail و student dashboard.)
#   - lesson       : درس تحصيلي (محتوى فقط للطالبة).
#   - comprehensive: اختبار شامل (فقط إن كان مفعّلاً).
#
# يُستثنى من الطالبة: bank (بنك أسئلة) — وكذلك الاختبارات بأنواعها.
STUDENT_VISIBLE_CONTENT = {'skill', 'lesson', 'comprehensive'}


def home(request):
    """
    الصفحة الرئيسية — تعرض المحتوى التعليمي + الاختبارات الشاملة.

    منطق العرض حسب الدور:
    - زائرة / طالبة → فقط: مهارات قدرات + دروس تحصيلي + شاملة مفعّلة.
      (لا تظهر بنوك الأسئلة ولا اختبارات التحصيلي).
    - معلمة / مديرة → كل المحتوى المفعّل + الشاملة (للإدارة).
    """
    settings_obj = SchoolSettings.objects.first()
    role = _get_role(request.user)

    base_qs = (
        TeacherSkill.objects
        .select_related('created_by')
        .order_by('-created_at')
    )

    if role in ('ADMIN', 'TEACHER'):
        # كل المحتوى الفعّال + الشاملة دائماً
        skills = base_qs.filter(
            Q(is_active=True) | Q(content_type='comprehensive')
        )
    else:
        # طالبة/زائرة: فلترة صارمة + إخفاء بنوك الأسئلة وأي اختبار غير شامل
        skills = base_qs.filter(
            content_type__in=STUDENT_VISIBLE_CONTENT,
        ).filter(
            Q(is_active=True) | Q(content_type='comprehensive', is_active=True)
        )

    return render(request, 'core/home.html', {
        'settings': settings_obj,
        'skills': skills,
        'classrooms': ClassRoom.objects.all(),
        'role': role,
    })


def skill_detail(request, skill_id):
    """
    تفاصيل المهارة/الدرس + الاختبارات.

    قيود الطالبة:
    - لا يحق لها رؤية اختبار قبلي/بعدي/درس/بنك إلا عبر "أداء الاختبار"
      المفعّل من المعلمة (تأخذ الرابط منها). هنا نعرض المحتوى التعليمي فقط.
    """
    skill = get_object_or_404(TeacherSkill, pk=skill_id)
    role = _get_role(request.user)

    exams = list(skill.exams.all())
    pre_exam = next((e for e in exams if e.exam_type == 'pre'), None)
    post_exam = next((e for e in exams if e.exam_type == 'post'), None)
    lesson_exam = next((e for e in exams if e.exam_type == 'lesson'), None)
    bank_exam = next((e for e in exams if e.exam_type == 'bank'), None)
    comp_exam = next(
        (e for e in exams if e.exam_type in ('comprehensive_qodrat', 'comprehensive_tahsili')),
        None,
    )

    # للطالبة/الزائرة: نخفي تفاصيل الاختبارات تماماً
    is_student = (role == 'STUDENT') or role is None
    if is_student:
        pre_exam = None
        post_exam = None
        lesson_exam = None
        bank_exam = None
        # نسمح برؤية الاختبار الشامل فقط إن كان مفعّلاً
        if comp_exam and not comp_exam.is_active:
            comp_exam = None

    return render(request, 'core/skill_detail.html', {
        'skill': skill,
        'pre_exam': pre_exam,
        'post_exam': post_exam,
        'lesson_exam': lesson_exam,
        'bank_exam': bank_exam,
        'comp_exam': comp_exam,
        'classrooms': ClassRoom.objects.all(),
        'role': role,
        'is_student': is_student,
    })


def take_test(request, skill_id):
    """عرض الاختبار القبلي العام (للزائر)."""
    skill = get_object_or_404(TeacherSkill, pk=skill_id)
    pre_exam = skill.exams.filter(exam_type='pre').first()
    questions = pre_exam.questions.all() if pre_exam else []
    return render(request, 'core/take_test.html', {
        'skill': skill,
        'questions': questions,
    })


def skill_print(request, skill_id):
    """نسخة قابلة للطباعة من المحتوى التعليمي للمهارة/الدرس."""
    skill = get_object_or_404(TeacherSkill, pk=skill_id)
    content = getattr(skill, 'content', None)
    return render(request, 'core/skill_print.html', {
        'skill': skill,
        'content': content,
        'settings': SchoolSettings.objects.first(),
    })


@login_required
def exam_print(request, exam_id):
    """
    نسخة قابلة للطباعة من الاختبار (مع/بدون الإجابات).
    - المعلمة/المديرة: تظهر الإجابات الصحيحة (نسخة المعلم).
    - الطالبة: نموذج فارغ بدون إجابات صحيحة.
    """
    exam = get_object_or_404(TeacherExam, pk=exam_id)
    role = _get_role(request.user)
    show_answers = role in ('ADMIN', 'TEACHER') and request.GET.get('answers') != '0'
    return render(request, 'core/exam_print.html', {
        'exam': exam,
        'questions': exam.questions.all().order_by('order'),
        'show_answers': show_answers,
        'settings': SchoolSettings.objects.first(),
    })


# ═══════════════════════════════════════════════════════════════
# تفعيل/إلغاء الاختبارات (AJAX)
# ═══════════════════════════════════════════════════════════════

@login_required
@require_POST
def activate_exam(request, exam_id):
    """
    تفعيل الاختبار لفصل محدد، أو لجميع الفصول إن كان classroom_id == 'all'.
    يولّد رابطاً مخصصاً + يسجّل حصة (للمعلمات).
    """
    exam = get_object_or_404(TeacherExam, pk=exam_id)
    classroom_id = (request.POST.get('classroom_id') or '').strip()
    if not classroom_id:
        return JsonResponse({'success': False, 'error': 'لم يُحدّد فصل'}, status=400)

    # تفعيل الاختبار نفسه
    exam.is_active = True
    exam.save(update_fields=['is_active'])

    # تخزين الفصول المستهدفة على المهارة الأم لتُعرض على الطالبة
    if classroom_id == 'all':
        target_text = 'جميع الفصول'
    else:
        cls = get_object_or_404(ClassRoom, pk=classroom_id)
        target_text = cls.name

    skill = exam.skill
    # نضمّن في target_classes (string) — توافقي مع باقي الكود
    skill.target_classes = target_text
    skill.is_active = True  # تفعيل المهارة لتظهر في الواجهة
    skill.save(update_fields=['target_classes', 'is_active'])

    # تسجيل حصة إذا كان من فعّل معلمة
    try:
        teacher = Teacher.objects.get(user=request.user)
        ClassSession.objects.get_or_create(
            teacher=teacher,
            skill=skill,
            session_type='qodrat' if skill.skill_type in ('qodrat_kamy', 'qodrat_lafzy') else 'tahsili',
            target_class=target_text,
            session_date=timezone.now().date(),
            defaults={
                'session_time': timezone.now().time(),
                'exam': exam,
            },
        )
    except Teacher.DoesNotExist:
        pass

    url = request.build_absolute_uri(f'/students/exam/{exam.id}/')
    return JsonResponse({
        'success': True,
        'url': url,
        'target': target_text,
        'message': f'✅ تم تفعيل {exam.get_exam_type_display()} — {target_text}',
    })


@login_required
@require_POST
def deactivate_exam(request, exam_id):
    """إلغاء تفعيل اختبار."""
    exam = get_object_or_404(TeacherExam, pk=exam_id)
    exam.is_active = False
    exam.save(update_fields=['is_active'])
    return JsonResponse({'success': True})


# ═══════════════════════════════════════════════════════════════
# لوحة المديرة
# ═══════════════════════════════════════════════════════════════

@admin_required
def admin_dashboard(request):
    """لوحة المديرة الرئيسية — إحصاءات + قوائم المعلمات والطالبات."""
    teacher_profiles = (
        Profile.objects
        .filter(role='TEACHER')
        .select_related('user')
        .annotate(
            skills_count=Count('user__teacher__teacher_skills', distinct=True),
            sessions_count=Count('user__teacher__sessions', distinct=True),
            avg_score=Avg('user__teacher__teacher_skills__exams__results__percentage'),
        )
    )
    teachers_data = [
        {
            'profile': p,
            'user': p.user,
            'name': (f"{p.user.first_name} {p.user.last_name}".strip() or p.user.username),
            'national_id': p.national_id,
            'pin_code': p.pin_code,
            'skills_count': p.skills_count or 0,
            'sessions_count': p.sessions_count or 0,
            'avg_score': round(p.avg_score or 0, 1),
            'last_login': p.user.last_login,
            'is_active': p.user.is_active,
        }
        for p in teacher_profiles
    ]

    student_profiles = (
        Profile.objects
        .filter(role='STUDENT')
        .select_related('user')
        .annotate(
            results_count=Count('user__teacher_exam_results', distinct=True),
            avg_score=Avg('user__teacher_exam_results__percentage'),
        )
    )
    students_data = [
        {
            'profile': p,
            'user': p.user,
            'name': (f"{p.user.first_name} {p.user.last_name}".strip() or p.user.username),
            'national_id': p.national_id,
            'results_count': p.results_count or 0,
            'avg_score': round(p.avg_score or 0, 1),
            'last_login': p.user.last_login,
            'is_active': p.user.is_active,
        }
        for p in student_profiles
    ]

    return render(request, 'core/admin_dashboard.html', {
        'total_teachers': len(teachers_data),
        'total_students': len(students_data),
        'total_skills': TeacherSkill.objects.filter(is_active=True).count(),
        'total_results': ExamResult.objects.count(),
        'teachers_data': teachers_data,
        'students_data': students_data,
        'classrooms': ClassRoom.objects.all().order_by('name'),
    })


# ─── إدارة المستخدمين ─────────────────────────────────────────

@admin_required
@require_POST
def admin_add_teacher(request):
    full_name = (request.POST.get('full_name') or '').strip()
    national_id = (request.POST.get('national_id') or '').strip()
    pin_code = (request.POST.get('pin_code') or '').strip()

    if not full_name or not national_id:
        messages.error(request, 'يرجى إدخال الاسم ورقم الهوية')
        return redirect('admin_dashboard')
    if not national_id.isdigit() or not (8 <= len(national_id) <= 12):
        messages.error(request, 'رقم هوية غير صالح (8-12 رقم)')
        return redirect('admin_dashboard')
    if pin_code and not pin_code.isdigit():
        messages.error(request, 'رمز PIN يجب أن يكون أرقاماً')
        return redirect('admin_dashboard')
    if User.objects.filter(username=national_id).exists():
        messages.error(request, 'رقم الهوية مسجّل مسبقاً')
        return redirect('admin_dashboard')

    name_parts = full_name.split()
    user = User.objects.create_user(
        username=national_id,
        password=pin_code or national_id,
        first_name=name_parts[0] if name_parts else full_name,
        last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
    )
    Profile.objects.create(
        user=user,
        role='TEACHER',
        national_id=national_id,
        pin_code=pin_code,
    )
    Teacher.objects.create(user=user, full_name=full_name)
    messages.success(request, f'✅ تم إضافة المعلمة {full_name}')
    return redirect('admin_dashboard')


@admin_required
@require_POST
def admin_add_student(request):
    full_name = (request.POST.get('full_name') or '').strip()
    national_id = (request.POST.get('national_id') or '').strip()
    classroom_id = (request.POST.get('classroom_id') or '').strip()

    if not full_name or not national_id:
        messages.error(request, 'يرجى إدخال الاسم ورقم الهوية')
        return redirect('admin_dashboard')
    if not national_id.isdigit() or not (8 <= len(national_id) <= 12):
        messages.error(request, 'رقم هوية غير صالح (8-12 رقم)')
        return redirect('admin_dashboard')
    if User.objects.filter(username=national_id).exists():
        messages.error(request, 'رقم الهوية مسجّل مسبقاً')
        return redirect('admin_dashboard')

    name_parts = full_name.split()
    user = User.objects.create_user(
        username=national_id,
        password=national_id,
        first_name=name_parts[0] if name_parts else full_name,
        last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
    )
    # ملاحظة: pin_code فارغ للطالبة → دخول بالهوية فقط (مطلوب).
    Profile.objects.create(
        user=user,
        role='STUDENT',
        national_id=national_id,
        pin_code='',
    )

    classroom = ClassRoom.objects.filter(id=classroom_id).first()
    if classroom:
        Student.objects.get_or_create(
            full_name=full_name,
            defaults={'classroom': classroom},
        )
    messages.success(request, f'✅ تم إضافة الطالبة {full_name}')
    return redirect('admin_dashboard')


@admin_required
@require_POST
def admin_delete_user(request, user_id):
    """حذف مستخدم — مع حماية الحساب الحالي و superuser."""
    target = User.objects.filter(id=user_id).first()
    if target is None:
        messages.error(request, 'المستخدم غير موجود')
        return redirect('admin_dashboard')
    if target.id == request.user.id:
        messages.error(request, 'لا يمكنك حذف حسابك أثناء الجلسة')
        return redirect('admin_dashboard')
    if target.is_superuser:
        messages.error(request, 'لا يمكن حذف حساب superuser')
        return redirect('admin_dashboard')

    name = target.get_full_name() or target.username
    target.delete()
    messages.success(request, f'🗑️ تم حذف {name}')
    return redirect('admin_dashboard')


@admin_required
@require_POST
def admin_edit_user(request, user_id):
    """تعديل بيانات مستخدم: الاسم + PIN + تفعيل/تعطيل."""
    target = get_object_or_404(User, id=user_id)
    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, 'لا يمكن تعديل حساب superuser')
        return redirect('admin_dashboard')

    full_name = (request.POST.get('full_name') or '').strip()
    pin_code = (request.POST.get('pin_code') or '').strip()
    action = request.POST.get('action') or 'save'

    if action == 'toggle':
        target.is_active = not target.is_active
        target.save(update_fields=['is_active'])
        messages.success(request, f"✅ تم {'تفعيل' if target.is_active else 'تعطيل'} الحساب")
        return redirect('admin_dashboard')

    if full_name:
        parts = full_name.split()
        target.first_name = parts[0] if parts else full_name
        target.last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
        target.save(update_fields=['first_name', 'last_name'])
        # نحدّث Teacher.full_name إن وُجد
        try:
            target.teacher.full_name = full_name
            target.teacher.save(update_fields=['full_name'])
        except Teacher.DoesNotExist:
            pass

    try:
        profile = target.core_profile
        if pin_code:
            if not pin_code.isdigit():
                messages.error(request, 'رمز PIN يجب أن يكون أرقاماً')
                return redirect('admin_dashboard')
            profile.pin_code = pin_code
        # نسمح بمسح PIN عبر إرسال "clear"
        if request.POST.get('clear_pin') == '1':
            profile.pin_code = ''
        profile.save(update_fields=['pin_code'])
    except Profile.DoesNotExist:
        pass

    messages.success(request, '✅ تم حفظ التعديلات')
    return redirect('admin_dashboard')


@admin_required
@require_POST
def admin_add_classroom(request):
    """إضافة فصل دراسي."""
    name = (request.POST.get('name') or '').strip()
    if not name:
        messages.error(request, 'يرجى إدخال اسم الفصل')
        return redirect('admin_dashboard')
    cls, created = ClassRoom.objects.get_or_create(name=name)
    if created:
        messages.success(request, f'✅ تم إضافة الفصل {name}')
    else:
        messages.warning(request, f'⚠️ الفصل {name} موجود مسبقاً')
    return redirect('admin_dashboard')


@admin_required
@require_POST
def admin_delete_classroom(request, classroom_id):
    cls = get_object_or_404(ClassRoom, id=classroom_id)
    name = cls.name
    cls.delete()
    messages.success(request, f'🗑️ تم حذف الفصل {name}')
    return redirect('admin_dashboard')


# ─── استيراد Excel للمعلمات ───────────────────────────────────

MAX_EXCEL_SIZE = 5 * 1024 * 1024


def _read_excel_or_msg(request, redirect_target):
    """يقرأ ملف Excel من الطلب ويرجع worksheet أو يعيد توجيه برسالة خطأ."""
    excel = request.FILES.get('excel_file')
    if not excel:
        messages.error(request, 'لم يُرفع ملف')
        return None
    if excel.size > MAX_EXCEL_SIZE:
        messages.error(request, 'حجم الملف يتجاوز 5 ميجا')
        return None
    if not excel.name.lower().endswith(('.xlsx', '.xlsm')):
        messages.error(request, 'الصيغة المدعومة: xlsx/xlsm')
        return None
    try:
        import openpyxl
        wb = openpyxl.load_workbook(excel, data_only=True)
        return wb.active
    except Exception as exc:
        messages.error(request, f'❌ تعذّر فتح الملف: {exc}')
        return None


@admin_required
@require_POST
def admin_import_teachers(request):
    """
    استيراد معلمات من Excel.
    أعمدة الملف المتوقعة: الاسم | رقم الهوية | PIN (اختياري)
    """
    ws = _read_excel_or_msg(request, 'admin_dashboard')
    if ws is None:
        return redirect('admin_dashboard')

    count, skipped = 0, []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        full_name = str(row[0]).strip() if row[0] else ''
        national_id = str(row[1]).strip() if len(row) > 1 and row[1] else ''
        pin = str(row[2]).strip() if len(row) > 2 and row[2] else ''

        if not full_name or not national_id:
            continue
        if not national_id.isdigit() or not (8 <= len(national_id) <= 12):
            skipped.append(f"{full_name}: هوية غير صالحة")
            continue
        if User.objects.filter(username=national_id).exists():
            skipped.append(f"{full_name}: مكرّر")
            continue

        try:
            parts = full_name.split()
            user = User.objects.create_user(
                username=national_id,
                password=pin or national_id,
                first_name=parts[0] if parts else full_name,
                last_name=' '.join(parts[1:]) if len(parts) > 1 else '',
            )
            Profile.objects.create(
                user=user, role='TEACHER',
                national_id=national_id, pin_code=pin,
            )
            Teacher.objects.create(user=user, full_name=full_name)
            count += 1
        except Exception as exc:
            skipped.append(f"{full_name}: {exc}")

    if skipped:
        messages.warning(
            request,
            f'✅ استُورد {count} معلمة • تم تخطّي {len(skipped)}: ' + ' | '.join(skipped[:5])
        )
    else:
        messages.success(request, f'✅ تم استيراد {count} معلمة')
    return redirect('admin_dashboard')


@admin_required
@require_POST
def admin_import_students(request):
    """
    استيراد طالبات من Excel.
    أعمدة الملف المتوقعة: الاسم | رقم الهوية | الفصل
    """
    ws = _read_excel_or_msg(request, 'admin_dashboard')
    if ws is None:
        return redirect('admin_dashboard')

    count, skipped = 0, []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        full_name = str(row[0]).strip() if row[0] else ''
        national_id = str(row[1]).strip() if len(row) > 1 and row[1] else ''
        classroom_name = str(row[2]).strip() if len(row) > 2 and row[2] else 'ث١٢'

        if not full_name or not national_id:
            continue
        if not national_id.isdigit() or not (8 <= len(national_id) <= 12):
            skipped.append(f"{full_name}: هوية غير صالحة")
            continue
        if User.objects.filter(username=national_id).exists():
            skipped.append(f"{full_name}: مكرّر")
            continue

        try:
            classroom, _ = ClassRoom.objects.get_or_create(name=classroom_name)
            parts = full_name.split()
            user = User.objects.create_user(
                username=national_id,
                password=national_id,
                first_name=parts[0] if parts else full_name,
                last_name=' '.join(parts[1:]) if len(parts) > 1 else '',
            )
            # PIN فارغ للطالبة → دخول بالهوية فقط
            Profile.objects.create(
                user=user, role='STUDENT',
                national_id=national_id, pin_code='',
            )
            Student.objects.get_or_create(
                full_name=full_name,
                defaults={'classroom': classroom},
            )
            count += 1
        except Exception as exc:
            skipped.append(f"{full_name}: {exc}")

    if skipped:
        messages.warning(
            request,
            f'✅ استُورد {count} طالبة • تم تخطّي {len(skipped)}: ' + ' | '.join(skipped[:5])
        )
    else:
        messages.success(request, f'✅ تم استيراد {count} طالبة')
    return redirect('admin_dashboard')


# ─── الدخول كمستخدم ──────────────────────────────────────────

@admin_required
@require_POST
def admin_view_as(request, user_id):
    target = get_object_or_404(User, id=user_id)
    target_role = _get_role(target)

    if target_role == 'ADMIN' or target.is_superuser:
        messages.error(request, 'لا يمكن الدخول كحساب إدارة آخر')
        return redirect('admin_dashboard')

    request.session['admin_id'] = request.user.id
    auth_login(request, target, backend='django.contrib.auth.backends.ModelBackend')

    if target_role == 'TEACHER':
        return redirect('teacher_dashboard')
    if target_role == 'STUDENT':
        return redirect('student_dashboard')
    return redirect('home')


@login_required
@require_POST
def admin_return(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('home')
    try:
        admin_user = User.objects.get(id=admin_id)
    except User.DoesNotExist:
        return redirect('home')

    auth_login(request, admin_user, backend='django.contrib.auth.backends.ModelBackend')
    request.session.pop('admin_id', None)
    return redirect('admin_dashboard')


# ─── الاختبارات الشاملة ──────────────────────────────────────

@admin_required
def admin_comprehensive(request):
    """قائمة الاختبارات الشاملة (قدرات/تحصيلي)."""
    comp_skills = (
        TeacherSkill.objects
        .filter(content_type='comprehensive')
        .select_related('created_by')
        .prefetch_related('exams')
        .order_by('-created_at')
    )
    return render(request, 'core/admin_comprehensive.html', {
        'comp_skills': comp_skills,
        'classrooms': ClassRoom.objects.all().order_by('name'),
    })


@admin_required
@require_POST
def admin_add_comprehensive(request):
    """إنشاء اختبار شامل جديد."""
    title = (request.POST.get('title') or '').strip()
    comp_type = (request.POST.get('comp_type') or '').strip()

    if not title:
        messages.error(request, 'يرجى إدخال عنوان الاختبار')
        return redirect('admin_comprehensive')
    if comp_type not in ('qodrat_kamy', 'tahsili'):
        messages.error(request, 'يرجى اختيار نوع الاختبار (قدرات/تحصيلي)')
        return redirect('admin_comprehensive')

    duration = _safe_int(request.POST.get('duration'), default=120, minimum=1, maximum=600)
    questions_count = _safe_int(request.POST.get('questions_count'), default=60, minimum=1, maximum=300)
    pass_score = _safe_int(request.POST.get('pass_score'), default=50, minimum=0, maximum=100)

    teacher, _ = Teacher.objects.get_or_create(
        user=request.user,
        defaults={'full_name': request.user.get_full_name() or 'المديرة'},
    )

    skill = TeacherSkill.objects.create(
        content_type='comprehensive',
        title=title,
        skill_type=comp_type,
        description=request.POST.get('description', ''),
        created_by=teacher,
        target_classes='جميع الفصول',
        is_active=False,
    )
    TeacherExam.objects.create(
        skill=skill,
        exam_type='comprehensive_qodrat' if comp_type == 'qodrat_kamy' else 'comprehensive_tahsili',
        questions_count=questions_count,
        duration_minutes=duration,
        pass_score=pass_score,
        is_active=False,
    )
    messages.success(request, f'✅ تم إنشاء "{title}" — يمكنك إضافة الأسئلة من زر "الأسئلة".')
    return redirect('admin_comprehensive')


@admin_required
@require_POST
def admin_edit_comprehensive(request, skill_id):
    """تعديل اختبار شامل (العنوان/المدة/الأسئلة/درجة النجاح)."""
    skill = get_object_or_404(TeacherSkill, pk=skill_id, content_type='comprehensive')
    exam = skill.exams.first()

    title = (request.POST.get('title') or '').strip()
    if title:
        skill.title = title
    skill.description = request.POST.get('description', skill.description)
    skill.save(update_fields=['title', 'description'])

    if exam:
        exam.questions_count = _safe_int(request.POST.get('questions_count'), exam.questions_count, minimum=1, maximum=300)
        exam.duration_minutes = _safe_int(request.POST.get('duration'), exam.duration_minutes, minimum=1, maximum=600)
        exam.pass_score = _safe_int(request.POST.get('pass_score'), exam.pass_score, minimum=0, maximum=100)
        exam.save(update_fields=['questions_count', 'duration_minutes', 'pass_score'])

    messages.success(request, '✅ تم حفظ التعديلات')
    return redirect('admin_comprehensive')


@admin_required
@require_POST
def admin_delete_comprehensive(request, skill_id):
    """حذف اختبار شامل (يحذف الأسئلة + النتائج المرتبطة بفعل CASCADE)."""
    skill = get_object_or_404(TeacherSkill, pk=skill_id, content_type='comprehensive')
    title = skill.title
    skill.delete()
    messages.success(request, f'🗑️ تم حذف "{title}"')
    return redirect('admin_comprehensive')
