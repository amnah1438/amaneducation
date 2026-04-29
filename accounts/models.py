# Accounts app: منطق الدخول فقط — البيانات الفعلية للمستخدم في core.Profile.
#
# سابقاً كان هنا UserRole TextChoices بقيم lowercase (admin/teacher/student)
# بينما core.Profile.USER_ROLES يستخدم UPPERCASE (ADMIN/TEACHER/STUDENT).
# الازدواجية كانت تربك التطوير ومصدراً محتملاً لأخطاء مقارنة.
# نحذفها لمصلحة Source of Truth واحد في core.Profile.

# (لا توجد نماذج هنا — جميع البيانات في core.Profile)
