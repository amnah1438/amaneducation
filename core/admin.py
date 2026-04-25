from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import SchoolSettings, Profile

# ═══════════════════════════════════════
# إعدادات لوحة الأدمن
# ═══════════════════════════════════════
admin.site.site_header = "🎓 إدارة منصة آمنة التعليمية"
admin.site.site_title = "منصة آمنة"
admin.site.index_title = "لوحة التحكم الرئيسية"

# إخفاء Groups — مو محتاجينها
admin.site.unregister(Group)


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
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'national_id')
    list_filter = ('role',)
    search_fields = ('user__username', 'national_id')
    list_editable = ('role',)
    from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import SchoolSettings, Profile

admin.site.site_header = "🎓 إدارة منصة آمنة التعليمية"
admin.site.site_title = "منصة آمنة"
admin.site.index_title = "لوحة التحكم الرئيسية"

admin.site.unregister(Group)


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
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'national_id')
    list_filter = ('role',)
    search_fields = ('user__username', 'national_id')
    list_editable = ('role',)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('import-students/', 
                 self.admin_site.admin_view(self.import_students_view),
                 name='import_students'),
        ]
        return custom + urls
    
    def import_students_view(self, request):
        from django.shortcuts import redirect
        return redirect('/students/import/')