from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, JobSeekerProfile


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """
    Django Admin customization for the Custom User Model.
    """
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Permissions', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Selection', {'fields': ('role', 'email')}),
    )


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'location', 'has_resume', 'updated_at')
    search_fields = ('user__username', 'user__email', 'full_name', 'skills', 'location')
    list_filter = ('created_at', 'updated_at')

    def has_resume(self, obj):
        return obj.has_resume
    has_resume.boolean = True
