from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import SchoolSettings, Profile

admin.site.site_header = "🎓 إدارة منصة آمنة التعليمية"
admin.site.site_title = "منصة آمنة"
admin.site.index_title = "لوحة التحكم"

# إخفاء ما لا نحتاجه
try:
    admin.site.unregister(User)
except: pass
try:
    admin.site.unregister(Group)
except: pass


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ('platform_name', 'principal_name', 'updated_at')
    fieldsets = (
        ('الهوية الرسمية', {
            'fields': ('platform_name', 'principal_name', 'developer_name')
        }),
        ('الديباجة', {
            'fields': ('header_line_1', 'header_line_2', 'header_line_3', 'header_line_4')
        }),
        ('الشعارات', {
            'fields': ('ministry_logo', 'school_logo')
        }),
        ('الألوان', {
            'fields': ('primary_color',)
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'role', 'national_id', 'get_last_login')
    list_filter = ('role',)
    search_fields = ('user__first_name', 'user__last_name', 'national_id')
    readonly_fields = ('user', 'role', 'national_id')

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    get_full_name.short_description = 'الاسم'

    def get_last_login(self, obj):
        return obj.user.last_login.strftime('%Y/%m/%d') if obj.user.last_login else '—'
    get_last_login.short_description = 'آخر دخول'

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False