from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company',
        'created_by',
        'category',
        'job_type',
        'experience_level',
        'status',
        'application_deadline',
        'created_at'
    )
    list_filter = ('status', 'category', 'job_type', 'experience_level', 'created_at')
    search_fields = ('title', 'description', 'required_skills', 'company__company_name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    actions = ['mark_as_published', 'mark_as_closed']

    @admin.action(description="Mark selected jobs as Published")
    def mark_as_published(self, request, queryset):
        queryset.update(status='PUBLISHED')

    @admin.action(description="Mark selected jobs as Closed")
    def mark_as_closed(self, request, queryset):
        queryset.update(status='CLOSED')
