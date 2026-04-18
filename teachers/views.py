from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
import json
import logging

# Models
from .models import TeacherSkill, TeacherSkillContent, TeacherExam, TeacherQuestion

logger = logging.getLogger(__name__)


# =========================
# 🔹 Helper Functions
# =========================

def safe_int(value, default):
    """تحويل آمن للأرقام"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def check_teacher(request):
    """التحقق أن المستخدم معلمة"""
    return hasattr(request.user, 'teacher')


def get_teacher(request):
    """جلب حساب المعلمة"""
    return getattr(request.user, 'teacher', None)


# =========================
# 🔹 Dashboard (تم إضافتها ✅)
# =========================

@login_required
def teacher_dashboard(request):
    """صفحة لوحة تحكم المعلمة"""
    return render(request, 'teachers/dashboard.html')


# =========================
# 🔹 Add Skill
# =========================

@login_required
@transaction.atomic
def add_skill_complete(request):
    """إضافة مهارة كاملة مع اختباراتها وأسئلتها"""

    # تحقق من المعلمة
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

        content_type = request.POST.get('content_type', 'skill')
        is_active = request.POST.get('is_active') == 'on'

        try:
            # ١ — إنشاء المهارة
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

            # ٢ — محتوى الشرح
            video_url = request.POST.get('video_url', '')
            plain_text = request.POST.get('plain_text', '')

            if video_url or plain_text:
                TeacherSkillContent.objects.create(
                    skill=skill,
                    video_url=video_url,
                    plain_text=plain_text,
                )

            # ===== مهارة (قبلي + بعدي) =====
            if content_type == 'skill':

                pre_exam = TeacherExam.objects.create(
                    skill=skill,
                    exam_type='pre',
                    questions_count=safe_int(request.POST.get('pre_count'), 10),
                    duration_minutes=safe_int(request.POST.get('pre_time'), 15),
                    pass_score=safe_int(request.POST.get('pre_pass'), 60),
                    delivery=request.POST.get('pre_delivery', 'both'),
                    is_active=is_active,
                )

                save_questions(request, pre_exam, 'pre_questions')

                post_exam = TeacherExam.objects.create(
                    skill=skill,
                    exam_type='post',
                    questions_count=safe_int(request.POST.get('post_count'), 10),
                    duration_minutes=safe_int(request.POST.get('post_time'), 15),
                    pass_score=safe_int(request.POST.get('post_pass'), 70),
                    delivery=request.POST.get('post_delivery', 'both'),
                    is_active=is_active,
                )

                save_questions(request, post_exam, 'post_questions')

            # ===== درس أو بنك =====
            elif content_type in ['lesson', 'bank']:

                lesson_exam = TeacherExam.objects.create(
                    skill=skill,
                    exam_type='lesson' if content_type == 'lesson' else 'bank',
                    questions_count=safe_int(request.POST.get('pre_count'), 10),
                    duration_minutes=safe_int(request.POST.get('pre_time'), 15),
                    pass_score=safe_int(request.POST.get('pre_pass'), 60),
                    is_active=is_active,
                )

                save_questions(request, lesson_exam, 'pre_questions', with_skill=True)

            messages.success(request, f'✅ تم حفظ "{title}" بنجاح')
            return redirect('skill_manager')

        except Exception as e:
            logger.error(f"Error saving skill: {str(e)}")
            messages.error(request, 'حدث خطأ أثناء الحفظ، حاول مرة أخرى')
            return redirect('skill_manager')

    return redirect('skill_manager')


# =========================
# 🔹 Save Questions
# =========================

def save_questions(request, exam, field_name, with_skill=False):
    """حفظ الأسئلة بطريقة منظمة"""

    try:
        questions = json.loads(request.POST.get(field_name, '[]'))

        for i, q in enumerate(questions):
            TeacherQuestion.objects.create(
                exam=exam,
                order=i + 1,
                question_plain=q.get('text', ''),
                option_a_plain=q.get('a', ''),
                option_b_plain=q.get('b', ''),
                option_c_plain=q.get('c', ''),
                option_d_plain=q.get('d', ''),
                correct_answer=q.get('correct', 'A'),
                feedback_plain=q.get('feedback', ''),
                target_skill_name=q.get('skill', '') if with_skill else '',
            )

    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON in {field_name}")