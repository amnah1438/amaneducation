"""
Core views — الواجهة الأمامية + لوحة المديرة.

الإصلاحات الرئيسية:
1) حذف التعريف المكرر للدالة admin_add_classroom (كان معرفاً مرتين فيختفي الأول).
2) استبدال bare-except بفلترة استثناءات محددة (Profile.DoesNotExist, ValueError, …).
3) دالة decorator موحّدة @admin_required بدلاً من تكرار try/except في كل view.
4) تحويل admin_view_as إلى POST + منع التحول إلى مدير آخر (صلاحيات).
5) منع crash في admin_add_comprehensive عند إدخال قيم غير رقمية في duration/pass_score.
6) استخدام select_related/annotate لتقليل N+1 queries في admin_dashboard.
"""
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.models import Profile, SchoolSettings
from students.models import ClassRoom
from teachers.models import (
    ClassSession,
    ExamResult,
    Teacher,
    TeacherExam,
    TeacherSkill,
)


# ═══════════════════════════════════════════════════════════════
# Decorators وأدوات صلاحيات
# ═══════════════════════════════════════════════════════════════

def _get_role(user):
    """يرجع دور المستخدم (ADMIN/TEACHER/STUDENT) أو None."""
    try:
        return user.core_profile.role
    except Profile.DoesNotExist:
        return None


def admin_required(view_func):
    """
    decorator: يضمن أن المستخدم مسجل دخول ودوره ADMIN.
    superuser يُسمح له تلقائياً (لتمكين الإدارة من Django admin).
    """
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.is_superuser or _get_role(request.user) == 'ADMIN':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'هذه الصفحة مخصصة للإدارة فقط.')
        return redirect('home')
    return _wrapped


def _safe_int(value, default, minimum=None, maximum=None):
    """
    يحول النص إلى int بأمان مع حدود اختيارية.
    استبدال لـ int(request.POST.get('x', N)) الذي يطرح ValueError إذا أُرسل نص فارغ.
    """
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
# الصفحات العامة
# ═══════════════════════════════════════════════════════════════

def home(request):
    """الصفحة الرئيسية — تعرض المهارات النشطة + الاختبارات الشاملة."""
    settings_obj = SchoolSettings.objects.first()
    all_skills = (
        TeacherSkill.objects
        .filter(Q(is_active=True) | Q(content_type='comprehensive'))
        .select_related('created_by')  # تقليل N+1 عند عرض اسم المعلمة
        .order_by('-created_at')
    )
    return render(request, 'core/home.html', {
        'settings': settings_obj,
        'skills': all_skills,
        'classrooms': ClassRoom.objects.all(),
    })


def skill_detail(request, skill_id):
    """تفاصيل مهارة + اختباراتها (قبلي/بعدي)."""
    skill = get_object_or_404(TeacherSkill, pk=skill_id)
    exams = list(skill.exams.all())  # نحوّلها list لتجنب استعلامات متعددة
    return render(request, 'core/skill_detail.html', {
        'skill': skill,
        'pre_exam': next((e for e in exams if e.exam_type == 'pre'), None),
        'post_exam': next((e for e in exams if e.exam_type == 'post'), None),
        'classrooms': ClassRoom.objects.all(),
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


# ═══════════════════════════════════════════════════════════════
# تفعيل/إلغاء الاختبارات (AJAX)
# ═══════════════════════════════════════════════════════════════

@login_required
@require_POST  # نمنع GET لمنع CSRF عبر <img>/<a>
def activate_exam(request, exam_id):
    """تفعيل الاختبار لفصل محدد + توليد رابط مخصّص."""
    exam = get_object_or_404(TeacherExam, pk=exam_id)
    classroom_id = request.POST.get('classroom_id')
    if not classroom_id:
        return JsonResponse({'success': False, 'error': 'لم يُحدّد فصل'}, status=400)

    classroom = get_object_or_404(ClassRoom, pk=classroom_id)
    exam.is_active = True
    exam.save(update_fields=['is_active'])

    # تسجيل حصة — استثناءات محددة بدل bare except
    try:
        teacher = Teacher.objects.get(user=request.user)
        ClassSession.objects.get_or_create(
            teacher=teacher,
            skill=exam.skill,
            session_type='qodrat' if exam.skill.skill_type in ['qodrat_kamy', 'qodrat_lafzy'] else 'tahsili',
            target_class=classroom.name,
            session_date=timezone.now().date(),
            defaults={'session_time': timezone.now().time()},
        )
    except Teacher.DoesNotExist:
        pass  # المديرة قد لا يكون لديها حساب Teacher — لا بأس

    url = request.build_absolute_uri(f'/students/exam/{exam.id}/')
    return JsonResponse({
        'success': True,
        'url': url,
        'message': f'✅ تم تفعيل {exam.get_exam_type_display()} للفصل {classroom.name}',
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
    """
    لوحة المديرة الرئيسية — إحصاءات + قوائم المعلمات والطالبات.

    الإصلاحات الجوهرية:
    - استبدال loop بـ select_related + annotate لتقليل عدد الاستعلامات
      من O(n*4) إلى O(1) لكل قائمة.
    """
    # ── المعلمات ── (annotate في استعلام واحد بدل حلقة)
    teacher_profiles = (
        Profile.objects
        .filter(role='TEACHER')
        .select_related('user')
        .annotate(
            skills_count=Count(
                'user__teacher__teacher_skills',
                distinct=True,
            ),
            sessions_count=Count('user__teacher__sessions', distinct=True),
            avg_score=Avg('user__teacher__teacher_skills__exams__results__percentage'),
        )
    )
    teachers_data = [
        {
            'profile': p,
            'user': p.user,
            'name': (f"{p.user.first_name} {p.user.last_name}".strip()
                     or p.user.username),
            'national_id': p.national_id,
            'skills_count': p.skills_count or 0,
            'sessions_count': p.sessions_count or 0,
            'avg_score': round(p.avg_score or 0, 1),
            'last_login': p.user.last_login,
        }
        for p in teacher_profiles
    ]

    # ── الطالبات ──
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
            'name': (f"{p.user.first_name} {p.user.last_name}".strip()
                     or p.user.username),
            'national_id': p.national_id,
            'results_count': p.results_count or 0,
            'avg_score': round(p.avg_score or 0, 1),
            'last_login': p.user.last_login,
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
        'classrooms': ClassRoom.objects.all(),
    })


# ─── إدارة المستخدمات ───────────────────────────────────────────

@admin_required
@require_POST  # GET للنماذج خطر — نقبل POST فقط
def admin_add_teacher(request):
    full_name = (request.POST.get('full_name') or '').strip()
    national_id = (request.POST.get('national_id') or '').strip()

    # تحقق صارم من المدخلات
    if not full_name or not national_id:
        messages.error(request, 'يرجى إدخال الاسم ورقم الهوية')
        return redirect('admin_dashboard')
    if not national_id.isdigit() or not (8 <= len(national_id) <= 12):
        messages.error(request, 'رقم هوية غير صالح')
        return redirect('admin_dashboard')
    if User.objects.filter(username=national_id).exists():
        messages.error(request, 'رقم الهوية مسجّل مسبقاً')
        return redirect('admin_dashboard')

    name_parts = full_name.split()
    user = User.objects.create_user(
        username=national_id,
        password=national_id,  # كلمة مرور أولية = الهوية، يجب تغييرها
        first_name=name_parts[0] if name_parts else full_name,
        last_name=' '.join(name_parts[1:]) if len(name_parts) > 1 else '',
    )
    Profile.objects.create(user=user, role='TEACHER', national_id=national_id)
    Teacher.objects.create(user=user, full_name=full_name)
    messages.success(request, f'✅ تم إضافة المعلمة {full_name}')
    return redirect('admin_dashboard')


@admin_required
@require_POST
def admin_add_student(request):
    from students.models import Student  # import محلي لكسر دائرة محتملة

    full_name = (request.POST.get('full_name') or '').strip()
    national_id = (request.POST.get('national_id') or '').strip()
    classroom_id = request.POST.get('classroom_id') or ''

    if not full_name or not national_id:
        messages.error(request, 'يرجى إدخال الاسم ورقم الهوية')
        return redirect('admin_dashboard')
    if not national_id.isdigit() or not (8 <= len(national_id) <= 12):
        messages.error(request, 'رقم هوية غير صالح')
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
    Profile.objects.create(user=user, role='STUDENT', national_id=national_id)

    classroom = ClassRoom.objects.filter(id=classroom_id).first()
    if classroom:
        Student.objects.create(full_name=full_name, classroom=classroom)
    messages.success(request, f'✅ تم إضافة الطالبة {full_name}')
    return redirect('admin_dashboard')


@admin_required
@require_POST  # حذف يجب أن يكون POST دائماً (CSRF + idempotency)
def admin_delete_user(request, user_id):
    """
    حذف مستخدم. لا تسمح بحذف:
    - حساب المديرة الحالية (لتجنّب قفل الباب على نفسها)
    - أي superuser
    """
    target = User.objects.filter(id=user_id).first()
    if target is None:
        messages.error(request, 'المستخدم غير موجود')
        return redirect('admin_dashboard')
    if target.id == request.user.id:
        messages.error(request, 'لا يمكنك حذف حسابك أثناء الجلسة')
        return redirect('admin_dashboard')
    if target.is_superuser:
        messages.error(request, 'لا يمكن حذف حساب superuser من هنا')
        return redirect('admin_dashboard')

    name = target.get_full_name() or target.username
    target.delete()
    messages.success(request, f'🗑️ تم حذف {name}')
    return redirect('admin_dashboard')


@admin_required
@require_POST
def admin_add_classroom(request):
    """إضافة فصل دراسي (وحيد، لا تكرار)."""
    name = (request.POST.get('name') or '').strip()
    if name:
        ClassRoom.objects.get_or_create(name=name)
        messages.success(request, f'✅ تم إضافة الفصل {name}')
    else:
        messages.error(request, 'يرجى إدخال اسم الفصل')
    return redirect('admin_dashboard')


# ─── الدخول كمستخدم ──────────────────────────────────────────────

@admin_required
@require_POST  # كان GET → ثغرة CSRF (يمكن سرقة الجلسة بصورة مدسوسة)
def admin_view_as(request, user_id):
    """
    تتيح للمديرة الدخول كأي معلمة/طالبة لتفقد ما تراه.
    قيود الأمان:
    - لا يُسمح بالدخول إلى حساب ADMIN آخر (منع امتياز جانبي).
    - نخزّن admin_id في الجلسة للعودة لاحقاً.
    """
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
    """العودة من جلسة view-as إلى حساب المديرة الأصلي."""
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


# ─── الاختبارات الشاملة ──────────────────────────────────────────

@admin_required
def admin_comprehensive(request):
    """قائمة الاختبارات الشاملة (قدرات/تحصيلي)."""
    comp_skills = (
        TeacherSkill.objects
        .filter(content_type='comprehensive')
        .select_related('created_by')
        .order_by('-created_at')
    )
    return render(request, 'core/admin_comprehensive.html', {
        'comp_skills': comp_skills,
        'classrooms': ClassRoom.objects.all(),
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

    # _safe_int يمنع crash عند إدخال نص فارغ أو غير رقمي
    duration = _safe_int(request.POST.get('duration'), default=120, minimum=1, maximum=600)
    questions_count = _safe_int(request.POST.get('questions_count'), default=60, minimum=1, maximum=300)
    pass_score = _safe_int(request.POST.get('pass_score'), default=50, minimum=0, maximum=100)

    # نضمن وجود حساب Teacher للمديرة لتمرير created_by
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
    messages.success(request, f'✅ تم إنشاء {title}')
    return redirect('admin_comprehensive')
