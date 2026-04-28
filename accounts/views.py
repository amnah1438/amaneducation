from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from core.models import Profile


def login_view(request):
    """صفحة تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    error = None

    if request.method == 'POST':
        login_type = request.POST.get('login_type')

        # دخول المديرة
        if login_type == 'admin':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user and hasattr(user, 'core_profile') and user.core_profile.role == 'ADMIN':
                login(request, user)
                return redirect_by_role(user)
            else:
                error = 'اسم المستخدم أو كلمة المرور غلط'

        # دخول المعلمة أو الطالبة برقم الهوية
        elif login_type == 'id':
            national_id = request.POST.get('national_id')
            try:
                profile = Profile.objects.get(national_id=national_id)
                login(request, profile.user)
                return redirect_by_role(profile.user)
            except Profile.DoesNotExist:
                error = 'رقم الهوية غير موجود'

    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    """تسجيل الخروج"""
    logout(request)
    return redirect('login')


def redirect_by_role(user):
    try:
        role = user.core_profile.role
        if role == 'ADMIN':
            return redirect('admin_dashboard')  # ← غيّري من 'home'
        elif role == 'TEACHER':
            return redirect('teacher_dashboard')
        elif role == 'STUDENT':
            return redirect('student_dashboard')
    except:
        return redirect('home')