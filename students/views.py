from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from teachers.models import (
    TeacherSkill, TeacherExam, TeacherQuestion,
    ExamResult, StudentAnswer
)
from .models import Student, ClassRoom


def get_student(request):
    try:
        return Student.objects.get(
            full_name__icontains=request.user.get_full_name()
        )
    except:
        return None


def check_student(request):
    try:
        profile = request.user.core_profile
        return profile.role == 'STUDENT'
    except:
        return False


# ═══════════════════════════════════════
# استيراد الطالبات
# ═══════════════════════════════════════

@login_required
def import_students_excel(request):
    try:
        profile = request.user.core_profile
        if profile.role not in ['ADMIN', 'TEACHER']:
            return redirect('home')
    except:
        return redirect('home')

    if request.method == 'POST' and request.FILES.get('excel_file'):
        import openpyxl
        from django.contrib.auth.models import User
        from core.models import Profile

        try:
            wb = openpyxl.load_workbook(request.FILES['excel_file'])
            ws = wb.active
            count = 0
            errors = []

            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row[0]:
                    continue

                full_name = str(row[0]).strip() if row[0] else ''
                national_id = str(row[1]).strip() if row[1] else ''
                classroom_name = str(row[2]).strip() if len(row) > 2 and row[2] else 'ث١٢'

                if not full_name or not national_id:
                    continue

                try:
                    classroom, _ = ClassRoom.objects.get_or_create(name=classroom_name)
                    Student.objects.get_or_create(
                        full_name=full_name,
                        defaults={'classroom': classroom}
                    )
                    if not User.objects.filter(username=national_id).exists():
                        user = User.objects.create_user(
                            username=national_id,
                            password=national_id,
                        )
                        Profile.objects.create(
                            user=user,
                            role='STUDENT',
                            national_id=national_id,
                        )
                        count += 1
                except Exception as e:
                    errors.append(f'{full_name}: {str(e)}')

            if errors:
                messages.warning(request, f'✅ تم استيراد {count} طالبة مع {len(errors)} أخطاء')
            else:
                messages.success(request, f'✅ تم استيراد {count} طالبة بنجاح!')

        except Exception as e:
            messages.error(request, f'❌ خطأ في الملف: {str(e)}')

    return render(request, 'students/import_students.html')


# ═══════════════════════════════════════
# داشبورد الطالبة
# ═══════════════════════════════════════

@login_required
def student_dashboard(request):
    if not check_student(request):
        return redirect('home')

    my_results = ExamResult.objects.filter(
        student=request.user
    ).select_related('exam', 'exam__skill').order_by('-submitted_at')

    total_exams = my_results.count()
    passed_exams = my_results.filter(passed=True).count()
    avg_score = 0
    if my_results.exists():
        avg_score = round(
            sum(r.percentage for r in my_results) / total_exams, 1
        )

    done_exam_ids = my_results.values_list('exam_id', flat=True)
    available_exams = TeacherExam.objects.filter(
        is_active=True
    ).exclude(id__in=done_exam_ids).select_related('skill')

    context = {
        'my_results': my_results[:10],
        'available_exams': available_exams,
        'total_exams': total_exams,
        'passed_exams': passed_exams,
        'avg_score': avg_score,
    }
    return render(request, 'students/dashboard.html', context)


# ═══════════════════════════════════════
# حل الاختبار
# ═══════════════════════════════════════

@login_required
def take_exam(request, exam_id):
    if not check_student(request):
        return redirect('home')

    exam = get_object_or_404(TeacherExam, id=exam_id, is_active=True)

    if ExamResult.objects.filter(exam=exam, student=request.user).exists():
        messages.warning(request, '⚠️ لقد أدّيتِ هذا الاختبار مسبقاً')
        return redirect('student_dashboard')

    questions = exam.questions.all().order_by('order')

    if not questions:
        messages.error(request, '❌ لا توجد أسئلة في هذا الاختبار')
        return redirect('student_dashboard')

    if request.method == 'POST':
        score = 0
        total = questions.count()

        result = ExamResult.objects.create(
            exam=exam,
            student=request.user,
            total=total,
            score=0,
            percentage=0,
            passed=False,
            time_taken_seconds=int(request.POST.get('time_taken', 0)),
        )

        for question in questions:
            chosen = request.POST.get(f'q_{question.id}', '')
            is_correct = chosen == question.correct_answer
            if is_correct:
                score += 1
            StudentAnswer.objects.create(
                result=result,
                question=question,
                chosen_answer=chosen,
                is_correct=is_correct,
            )

        percentage = round((score / total * 100), 1) if total > 0 else 0
        result.score = score
        result.percentage = percentage
        result.passed = percentage >= exam.pass_score
        result.save()

        messages.success(request, f'✅ تم تسليم الاختبار — نتيجتك: {score}/{total}')
        return redirect('student_result_view', result_id=result.id)

    context = {
        'exam': exam,
        'questions': questions,
        'duration': exam.duration_minutes * 60,
    }
    return render(request, 'students/take_exam.html', context)


# ═══════════════════════════════════════
# نتيجة الطالبة
# ═══════════════════════════════════════

@login_required
def student_result_view(request, result_id):
    if not check_student(request):
        return redirect('home')

    result = get_object_or_404(
        ExamResult, id=result_id, student=request.user
    )
    answers = StudentAnswer.objects.filter(
        result=result
    ).select_related('question').order_by('question__order')

    context = {
        'result': result,
        'answers': answers,
    }
    return render(request, 'students/result.html', context)