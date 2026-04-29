"""
Views للدخول وتسجيل الخروج.

ملاحظات معمارية مهمة:
- المديرة: تدخل بـ (username + password) عبر authenticate الرسمي.
- المعلمة/الطالبة: تدخل بـ (national_id + pin_code).
  ✦ سابقاً كان الدخول برقم الهوية فقط بدون أي تحقق — وهذا ثغرة خطيرة
    لأن أي شخص يعرف رقم هوية أحد المستخدمين يمكنه انتحاله.
  ✦ الحل: نطلب pin_code (6 أرقام) من حقل Profile.pin_code.
    إذا لم يكن مضبوطاً للمستخدم نستخدم رقم الهوية نفسه ككلمة مرور
    (متطابق مع الإنشاء في core/views.create_user(password=national_id))
    حتى لا نكسر الحسابات الحالية، مع تشجيع تغييره لاحقاً.
- نمنع enumeration attacks برسالة خطأ موحّدة.
- نعيد ضبط مفتاح الجلسة بعد الدخول لمنع Session Fixation.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from core.models import Profile


GENERIC_ERROR = 'بيانات الدخول غير صحيحة'


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


@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    """صفحة تسجيل الدخول الموحّدة."""
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    error = None

    if request.method == 'POST':
        login_type = request.POST.get('login_type', '').strip()

        # ─── 1) دخول المديرة (username + password) ──────────────
        if login_type == 'admin':
            username = (request.POST.get('username') or '').strip()
            password = request.POST.get('password') or ''
            user = authenticate(request, username=username, password=password)

            # نتحقق أنه فعلاً ADMIN — لا يكفي أن يكون authenticate ناجحاً
            if user and _user_role(user) == 'ADMIN':
                login(request, user)
                request.session.cycle_key()  # تحصين ضد Session Fixation
                return _redirect_by_role(user)
            error = GENERIC_ERROR

        # ─── 2) دخول معلمة/طالبة (national_id + pin) ───────────
        elif login_type == 'id':
            national_id = (request.POST.get('national_id') or '').strip()
            pin = (request.POST.get('pin_code') or '').strip()

            # نقبل أرقام فقط لمنع SQL noise وإكساء وضوحاً
            if not national_id.isdigit() or not (8 <= len(national_id) <= 12):
                error = GENERIC_ERROR
            else:
                user = _authenticate_by_national_id(national_id, pin)
                if user is not None:
                    login(request, user)
                    request.session.cycle_key()
                    return _redirect_by_role(user)
                error = GENERIC_ERROR

        else:
            error = GENERIC_ERROR

    return render(request, 'accounts/login.html', {'error': error})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """تسجيل الخروج وإفراغ الجلسة كاملة."""
    logout(request)
    return redirect('login')


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

def _user_role(user):
    """يرجع الدور بأمان دون استثناء صامت."""
    try:
        return user.core_profile.role
    except Profile.DoesNotExist:
        return None


def _authenticate_by_national_id(national_id, pin):
    """
    يصادق المستخدم برقم الهوية + PIN.

    منطق التحقق:
    1) إن وُجد pin_code في Profile → نقارن به (المسار الموصى به).
    2) خلاف ذلك (الحسابات القديمة المنشأة قبل التحديث) → نقارن
       بكلمة مرور Django الفعلية، التي ضبطت = national_id عند الإنشاء.
       هذا يحافظ على عمل الحسابات الحالية دون كسرها.

    يُرجع User إذا نجح، وإلا None (دون تسريب أي تفاصيل).
    """
    if not pin:
        return None
    try:
        profile = Profile.objects.select_related('user').get(
            national_id=national_id,
            role__in=['TEACHER', 'STUDENT'],
        )
    except Profile.DoesNotExist:
        return None

    user = profile.user
    if not user.is_active:
        return None

    # المسار 1: PIN مضبوط
    if profile.pin_code:
        if profile.pin_code == pin:
            return user
        return None

    # المسار 2: مرجعية تاريخية — كلمة مرور Django (national_id افتراضاً)
    if check_password(pin, user.password):
        return user
    return None
