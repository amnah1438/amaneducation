@login_required
def add_skill_complete(request):
    """إضافة مهارة كاملة مع اختباراتها وأسئلتها"""
    if not check_teacher(request):
        return redirect('home')

    teacher = get_teacher(request)

    if not teacher:
        messages.error(request, 'لا يوجد حساب معلمة')
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        import json

        # ١ — حفظ المهارة
        content_type = request.POST.get('content_type', 'skill')
        title = request.POST.get('title', '').strip()

        if not title:
            messages.error(request, 'يرجى إدخال عنوان المهارة')
            return redirect('skill_manager')

        is_active = request.POST.get('is_active') == 'on'

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

        # ٢ — حفظ محتوى الشرح
        video_url = request.POST.get('video_url', '')
        plain_text = request.POST.get('plain_text', '')
        if video_url or plain_text:
            TeacherSkillContent.objects.create(
                skill=skill,
                video_url=video_url,
                plain_text=plain_text,
            )

        # ٣ — حفظ الاختبار القبلي وأسئلته
        if content_type in ['skill']:
            pre_exam = TeacherExam.objects.create(
                skill=skill,
                exam_type='pre',
                questions_count=int(request.POST.get('pre_count', 10)),
                duration_minutes=int(request.POST.get('pre_time', 15)),
                pass_score=int(request.POST.get('pre_pass', 60)),
                delivery=request.POST.get('pre_delivery', 'both'),
                is_active=is_active,
            )

            # أسئلة القبلي
            pre_questions = request.POST.get('pre_questions', '[]')
            try:
                pre_qs = json.loads(pre_questions)
                for i, q in enumerate(pre_qs):
                    TeacherQuestion.objects.create(
                        exam=pre_exam,
                        order=i+1,
                        question_plain=q.get('text', ''),
                        option_a_plain=q.get('a', ''),
                        option_b_plain=q.get('b', ''),
                        option_c_plain=q.get('c', ''),
                        option_d_plain=q.get('d', ''),
                        correct_answer=q.get('correct', 'A'),
                        feedback_plain=q.get('feedback', ''),
                    )
            except:
                pass

        # ٤ — حفظ الاختبار البعدي وأسئلته
        if content_type in ['skill']:
            post_exam = TeacherExam.objects.create(
                skill=skill,
                exam_type='post',
                questions_count=int(request.POST.get('post_count', 10)),
                duration_minutes=int(request.POST.get('post_time', 15)),
                pass_score=int(request.POST.get('post_pass', 70)),
                delivery=request.POST.get('post_delivery', 'both'),
                is_active=is_active,
            )

            post_questions = request.POST.get('post_questions', '[]')
            try:
                post_qs = json.loads(post_questions)
                for i, q in enumerate(post_qs):
                    TeacherQuestion.objects.create(
                        exam=post_exam,
                        order=i+1,
                        question_plain=q.get('text', ''),
                        option_a_plain=q.get('a', ''),
                        option_b_plain=q.get('b', ''),
                        option_c_plain=q.get('c', ''),
                        option_d_plain=q.get('d', ''),
                        correct_answer=q.get('correct', 'A'),
                        feedback_plain=q.get('feedback', ''),
                    )
            except:
                pass

        # ٥ — للتحصيلي والبنك — اختبار واحد فقط
        elif content_type in ['lesson', 'bank']:
            lesson_exam = TeacherExam.objects.create(
                skill=skill,
                exam_type='lesson' if content_type == 'lesson' else 'bank',
                questions_count=int(request.POST.get('pre_count', 10)),
                duration_minutes=int(request.POST.get('pre_time', 15)),
                pass_score=int(request.POST.get('pre_pass', 60)),
                is_active=is_active,
            )

            pre_questions = request.POST.get('pre_questions', '[]')
            try:
                pre_qs = json.loads(pre_questions)
                for i, q in enumerate(pre_qs):
                    TeacherQuestion.objects.create(
                        exam=lesson_exam,
                        order=i+1,
                        question_plain=q.get('text', ''),
                        option_a_plain=q.get('a', ''),
                        option_b_plain=q.get('b', ''),
                        option_c_plain=q.get('c', ''),
                        option_d_plain=q.get('d', ''),
                        correct_answer=q.get('correct', 'A'),
                        target_skill_name=q.get('skill', ''),
                        feedback_plain=q.get('feedback', ''),
                    )
            except:
                pass

        messages.success(request, f'✅ تم حفظ "{title}" بنجاح مع جميع الاختبارات!')
        return redirect('skill_manager')

    return redirect('skill_manager')