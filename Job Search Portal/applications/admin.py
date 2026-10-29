from django.contrib import admin
from .models import JobApplication, SavedJob


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_at', 'updated_at')
    list_filter = ('status', 'applied_at', 'job__company')
    search_fields = ('applicant__username', 'applicant__email', 'job__title', 'job__company__company_name')
    ordering = ('-applied_at',)


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    search_fields = ('user__username', 'job__title')
    list_filter = ('created_at',)
