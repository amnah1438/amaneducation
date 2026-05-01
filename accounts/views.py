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
INACTIVE_ACCOUNT = 'الحساب غير مفعّل — تواصلي مع المديرة'

# نحفظ رقم الهوية كما كتبتْه المديرة (عربي/لاتيني). لكن وقت المطابقة
# نجرّب الصيغتين كي تتمكن الطالبة من الدخول بأي صيغة كتبتْها.
_AR_TO_LA = str.maketrans({
    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
    '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
    '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
    '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
})
_LA_TO_AR = str.maketrans({
    '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
    '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
})


def _id_variants(value):
    """صيغ متعددة من رقم الهوية للبحث (الأصلي + لاتيني + عربي)."""
    if not value:
        return []
    s = str(value).strip()
    return list({s, s.translate(_AR_TO_LA), s.translate(_LA_TO_AR)})


def _is_valid_id(value):
    """8-12 رقماً سواء عربية أو لاتينية."""
    if not value:
        return False
    latin = str(value).translate(_AR_TO_LA).strip()
    return latin.isdigit() and 8 <= len(latin) <= 12


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
    """تحقق من صلاحية رقم الهوية — يقبل العربي واللاتيني."""
    return _is_valid_id(value)


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
                error = 'رقم الهوية يجب أن يكون من 8 إلى 12 رقماً'
            else:
                user, reason = _authenticate_student_verbose(national_id)
                if user is not None:
                    login(request, user)
                    request.session.cycle_key()
                    return _redirect_by_role(user)
                error = reason

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
    """مصادقة المعلمة برقم الهوية + PIN — يبحث بكلتا الصيغتين."""
    profile = Profile.objects.select_related('user').filter(
        national_id__in=_id_variants(national_id),
        role='TEACHER',
    ).first()
    if profile is None:
        return None

    user = profile.user
    if not user.is_active:
        return None

    # المسار 1: PIN مضبوط في Profile (نقبل PIN عربي/لاتيني)
    if profile.pin_code:
        if profile.pin_code in _id_variants(pin):
            return user
        return None

    # المسار 2: كلمة مرور Django (national_id افتراضاً)
    if check_password(pin, user.password):
        return user
    return None


def _authenticate_student_verbose(national_id):
    """
    مصادقة الطالبة + سبب الفشل واضح للمساعدة في التشخيص.
    يرجع (user, error_message). user = None إن فشل.
    """
    profile = Profile.objects.select_related('user').filter(
        national_id__in=_id_variants(national_id),
        role='STUDENT',
    ).first()
    if profile is None:
        return None, STUDENT_NOT_FOUND

    if not profile.user.is_active:
        return None, INACTIVE_ACCOUNT

    if profile.pin_code:
        return None, 'حسابكِ يستخدم رمز PIN — اضغطي تبويبة "معلمة" وأدخلي الهوية والـ PIN'

    return profile.user, ''


def _authenticate_student(national_id):
    user, _ = _authenticate_student_verbose(national_id)
    return user
