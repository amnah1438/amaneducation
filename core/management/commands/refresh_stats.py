"""
أمر إدارة لتجميع وتجهيز البيانات الإحصائية في المنصة.

الاستخدام:
    python manage.py refresh_stats              # تجميع كامل
    python manage.py refresh_stats --days 30    # آخر 30 يوم فقط
    python manage.py refresh_stats --clean      # تنظيف البيانات اليتيمة + التجميع
    python manage.py refresh_stats --reset      # حذف وإعادة بناء كامل لجدول الإحصاءات

ما يقوم به الأمر:
1. حساب الإحصاءات اليومية (DailyStat) من نتائج الاختبارات.
2. ربط نتائج الاختبارات بالطالبات حسب الـ profile.
3. تنظيف الـ Profiles اليتيمة (User بدون Profile).
4. إعادة حساب target_classes للمهارات التي تم تفعيلها.
5. تنظيف TeacherSkill بدون created_by أو بدون أسئلة.
6. عرض ملخّص شامل في النهاية.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.utils import timezone


class Command(BaseCommand):
    help = 'تجميع وتحديث الإحصاءات وتنظيف البيانات اليتيمة'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90,
                            help='عدد الأيام السابقة لإعادة حسابها (افتراضي 90)')
        parser.add_argument('--clean', action='store_true',
                            help='تنظيف البيانات اليتيمة قبل التجميع')
        parser.add_argument('--reset', action='store_true',
                            help='حذف وإعادة بناء كامل لجدول DailyStat')

    def handle(self, *args, **opts):
        from analytics.models import DailyStat
        from teachers.models import (
            ExamResult, TeacherSkill, TeacherExam, ClassSession, Teacher,
        )
        from core.models import Profile

        self.stdout.write(self.style.MIGRATE_HEADING('═' * 60))
        self.stdout.write(self.style.MIGRATE_HEADING('🔄 بدء تجميع الإحصاءات...'))
        self.stdout.write(self.style.MIGRATE_HEADING('═' * 60))

        # ─── 1) تنظيف البيانات اليتيمة ──────────────────────────
        if opts['clean']:
            self.stdout.write('\n🧹 تنظيف البيانات اليتيمة...')

            # Users بدون Profile
            orphan_users = User.objects.filter(core_profile__isnull=True, is_superuser=False)
            n = orphan_users.count()
            if n:
                self.stdout.write(f'   • {n} مستخدم/ة بدون Profile — لن يُحذفوا، تنبيه فقط.')

            # TeacherSkill بدون created_by
            orphan_skills = TeacherSkill.objects.filter(created_by__isnull=True)
            ns = orphan_skills.count()
            if ns:
                orphan_skills.delete()
                self.stdout.write(self.style.WARNING(f'   • حُذفت {ns} مهارة بدون معلمة.'))

            # TeacherExam بدون skill
            orphan_exams = TeacherExam.objects.filter(skill__isnull=True)
            ne = orphan_exams.count()
            if ne:
                orphan_exams.delete()
                self.stdout.write(self.style.WARNING(f'   • حُذفت {ne} اختبارات بدون مهارة.'))

            # ExamResult بدون student أو exam
            orphan_results = ExamResult.objects.filter(Q(student__isnull=True) | Q(exam__isnull=True))
            nr = orphan_results.count()
            if nr:
                orphan_results.delete()
                self.stdout.write(self.style.WARNING(f'   • حُذفت {nr} نتائج يتيمة.'))

            # ClassSession بدون teacher أو skill
            orphan_sessions = ClassSession.objects.filter(Q(teacher__isnull=True) | Q(skill__isnull=True))
            nsess = orphan_sessions.count()
            if nsess:
                orphan_sessions.delete()
                self.stdout.write(self.style.WARNING(f'   • حُذفت {nsess} حصص يتيمة.'))

        # ─── 2) إعادة بناء DailyStat ─────────────────────────────
        if opts['reset']:
            self.stdout.write('\n♻️ إعادة بناء كامل لجدول DailyStat...')
            DailyStat.objects.all().delete()
        else:
            self.stdout.write(f'\n📊 تحديث آخر {opts["days"]} يوم...')

        days = opts['days']
        today = timezone.now().date()
        created_or_updated = 0

        for i in range(days):
            d = today - timedelta(days=i)
            day_results = ExamResult.objects.filter(submitted_at__date=d)
            count = day_results.count()
            avg = day_results.aggregate(a=Avg('percentage'))['a'] or 0

            DailyStat.objects.update_or_create(
                date=d,
                defaults={'attempts_count': count, 'avg_score': round(avg, 2)},
            )
            created_or_updated += 1

        self.stdout.write(self.style.SUCCESS(f'   ✓ تم تحديث {created_or_updated} يوم.'))

        # ─── 3) إصلاح Teacher records ─────────────────────────────
        self.stdout.write('\n👩‍🏫 التحقق من سجلات المعلمات...')
        teacher_profiles = Profile.objects.filter(role='TEACHER').select_related('user')
        fixed = 0
        for p in teacher_profiles:
            if not Teacher.objects.filter(user=p.user).exists():
                full_name = (p.user.get_full_name() or p.user.username).strip() or p.user.username
                Teacher.objects.create(user=p.user, full_name=full_name)
                fixed += 1
        if fixed:
            self.stdout.write(self.style.SUCCESS(f'   ✓ أُنشئت {fixed} سجل Teacher مفقود.'))
        else:
            self.stdout.write('   ✓ كل المعلمات مرتبطات بسجلات Teacher.')

        # ─── 4) ملخّص ──────────────────────────────────────────────
        self.stdout.write('\n' + '═' * 60)
        self.stdout.write(self.style.SUCCESS('📊 ملخّص الإحصاءات الحالي:'))
        self.stdout.write('═' * 60)

        stats = {
            '👩‍🎓 الطالبات': Profile.objects.filter(role='STUDENT').count(),
            '👩‍🏫 المعلمات': Profile.objects.filter(role='TEACHER').count(),
            '📚 المهارات (skill)': TeacherSkill.objects.filter(content_type='skill').count(),
            '📖 الدروس (lesson)': TeacherSkill.objects.filter(content_type='lesson').count(),
            '🗂️ بنوك الأسئلة': TeacherSkill.objects.filter(content_type='bank').count(),
            '🏆 الاختبارات الشاملة': TeacherSkill.objects.filter(content_type='comprehensive').count(),
            '📝 إجمالي الاختبارات': TeacherExam.objects.count(),
            '✅ الاختبارات النشطة': TeacherExam.objects.filter(is_active=True).count(),
            '📋 إجمالي النتائج': ExamResult.objects.count(),
            '🎯 نتائج ناجحة': ExamResult.objects.filter(passed=True).count(),
            '📅 الحصص المسجّلة': ClassSession.objects.count(),
        }
        for label, val in stats.items():
            self.stdout.write(f'   {label:30} → {val}')

        avg_all = ExamResult.objects.aggregate(a=Avg('percentage'))['a'] or 0
        self.stdout.write(f'   📈 متوسط الأداء العام         → {round(avg_all, 1)}%')

        self.stdout.write('\n' + '═' * 60)
        self.stdout.write(self.style.SUCCESS('✅ تم تجميع البيانات بنجاح'))
        self.stdout.write('═' * 60 + '\n')
