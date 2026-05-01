"""
Views للدخول وتسجيل الخروج.

النموذج المعتمد:
- المديرة: username + password.
- المعلمة: national_id + pin_code (PIN إجباري — حماية أعلى).
- الطالبة: national_id فقط (دخول مبسّط، بدون PIN حالياً).

النظام مصمم بحيث يمكن لاحقاً تفعيل (ID + PIN) للطالبة بمجرد:
1) ضبط Profile.pin_code للطالبة (أي قيمة)؛ سيُجبَر النظام على طلبها.
أي: وجود pin_code على حساب طالبة ⇒ يُطلب وتُستخدم تبويبة المعلمة.
عدم وجوده ⇒ ID فقط (الوضع الحالي للجميع).

أمان:
- رسالة خطأ موحّدة (لا enumeration).
- session.cycle_key بعد الدخول (Session Fixation hardening).
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from core.models import Profile


GENERIC_ERROR = 'بيانات الدخول غير صحيحة'
STUDENT_NOT_FOUND = 'رقم الهوية غير مسجّل — تواصلي مع المعلمة'


def _redirect_by_role(user):
    """يحوّل المستخدم إلى لوحته حسب الدور."""
    try:
        role = user.core_profile.role
    except Profile.DoesNotExist:
        return redirect('home')

    if role == 'ADMIN':
        return redirect('admin_dashboard')
    if role == 'TEACHER':
        return redirect('teacher_dashboard')
    if role == 'STUDENT':
        return redirect('student_dashboard')
    return redirect('home')


def _user_role(user):
    """يرجع الدور بأمان دون استثناء صامت."""
    try:
        return user.core_profile.role
    except Profile.DoesNotExist:
        return None


def _valid_national_id(value):
    """تحقق من صلاحية رقم الهوية (8-12 رقماً عددياً)."""
    return value.isdigit() and 8 <= len(value) <= 12


@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    """صفحة تسجيل الدخول الموحّدة (3 تبويبات: مديرة/معلمة/طالبة)."""
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    error = None

    if request.method == 'POST':
        login_type = (request.POST.get('login_type') or '').strip()

        # ─── 1) دخول المديرة (username + password) ──────────────
        if login_type == 'admin':
            username = (request.POST.get('username') or '').strip()
            password = request.POST.get('password') or ''
            user = authenticate(request, username=username, password=password)
            if user and (_user_role(user) == 'ADMIN' or user.is_superuser):
                login(request, user)
                request.session.cycle_key()
                return _redirect_by_role(user)
            error = GENERIC_ERROR

        # ─── 2) دخول المعلمة (national_id + pin) ───────────────
        elif login_type == 'teacher':
            national_id = (request.POST.get('national_id') or '').strip()
            pin = (request.POST.get('pin_code') or '').strip()

            if not _valid_national_id(national_id) or not pin:
                error = GENERIC_ERROR
            else:
                user = _authenticate_teacher(national_id, pin)
                if user is not None:
                    login(request, user)
                    request.session.cycle_key()
                    return _redirect_by_role(user)
                error = GENERIC_ERROR

        # ─── 3) دخول الطالبة (national_id فقط) ─────────────────
        elif login_type == 'student':
            national_id = (request.POST.get('national_id') or '').strip()

            if not _valid_national_id(national_id):
                error = GENERIC_ERROR
            else:
                user = _authenticate_student(national_id)
                if user is None:
                    error = STUDENT_NOT_FOUND
                else:
                    login(request, user)
                    request.session.cycle_key()
                    return _redirect_by_role(user)

        else:
            error = GENERIC_ERROR

    return render(request, 'accounts/login.html', {'error': error})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """تسجيل الخروج وإفراغ الجلسة كاملة."""
    logout(request)
    return redirect('login')


# ═══════════════════════════════════════════════════════════════
# Authentication helpers
# ═══════════════════════════════════════════════════════════════

def _authenticate_teacher(national_id, pin):
    """مصادقة المعلمة برقم الهوية + PIN."""
    try:
        profile = Profile.objects.select_related('user').get(
            national_id=national_id,
            role='TEACHER',
        )
    except Profile.DoesNotExist:
        return None

    user = profile.user
    if not user.is_active:
        return None

    # المسار 1: PIN مضبوط في Profile
    if profile.pin_code:
        return user if profile.pin_code == pin else None

    # المسار 2: مرجعية تاريخية — كلمة مرور Django (national_id افتراضاً)
    if check_password(pin, user.password):
        return user
    return None


def _authenticate_student(national_id):
    """
    مصادقة الطالبة برقم الهوية فقط.

    منطق التوسعة المستقبلي:
    - إن كان pin_code مضبوطاً → نرفض الدخول هنا ونطلب من الطالبة استخدام
      تبويبة المعلمة (ID+PIN). هذا يتيح ترقية تدريجية بلا كسر.
    - إن لم يكن pin_code مضبوطاً → الدخول بالهوية فقط.
    """
    try:
        profile = Profile.objects.select_related('user').get(
            national_id=national_id,
            role='STUDENT',
        )
    except Profile.DoesNotExist:
        return None

    if not profile.user.is_active:
        return None

    # طالبة لها PIN → ترفض هنا، تستخدم تبويبة المعلمة (نفس الـ flow)
    if profile.pin_code:
        return None

    return profile.user
