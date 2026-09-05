"""
أمر إدارة لمرة واحدة — يربط سجلات Student بحسابات User عبر مطابقة الاسم.
شغّليه بعد تطبيق migration 0004:
    python manage.py link_students_to_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import Student


class Command(BaseCommand):
    help = 'ربط سجلات Student بحسابات User عبر مطابقة الاسم الكامل'

    def handle(self, *args, **options):
        linked = 0
        skipped = 0
        no_match = 0

        students = Student.objects.filter(user__isnull=True).select_related()
        student_users = User.objects.filter(
            core_profile__role='STUDENT'
        ).select_related('core_profile')

        # بناء قاموس اسم → user لتسريع البحث
        name_map = {}
        for u in student_users:
            full = f"{u.first_name} {u.last_name}".strip()
            if full:
                name_map.setdefault(full, []).append(u)

        for student in students:
            candidates = name_map.get(student.full_name, [])
            if len(candidates) == 1:
                u = candidates[0]
                # تحقق إنه ما مرتبط بطالبة ثانية
                if not Student.objects.filter(user=u).exists():
                    student.user = u
                    student.save(update_fields=['user'])
                    linked += 1
                    self.stdout.write(f'  ✓ ربطت: {student.full_name}')
                else:
                    skipped += 1
                    self.stdout.write(f'  ⚠ مكرر: {student.full_name}')
            elif len(candidates) > 1:
                skipped += 1
                self.stdout.write(f'  ⚠ تعدد: {student.full_name} ({len(candidates)} حسابات)')
            else:
                no_match += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nاكتمل: {linked} مرتبطة | {skipped} تخطّي | {no_match} بلا تطابق'
        ))
