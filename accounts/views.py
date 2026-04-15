from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm


def login_view(request):
    """صفحة تسجيل الدخول"""
    # لو المستخدم داخل أصلاً — وجّهه للصفحة المناسبة
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect_by_role(user)
            else:
                form.add_error(None, 'اسم المستخدم أو كلمة المرور غلط')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """تسجيل الخروج"""
    logout(request)
    return redirect('login')


def redirect_by_role(user):
    """توجيه المستخدم حسب دوره"""
    try:
        role = user.profile.role
        if role == 'admin':
            return redirect('admin_dashboard')
        elif role == 'teacher':
            return redirect('teacher_dashboard')
        elif role == 'student':
            return redirect('student_dashboard')
    except:
        return redirect('home')