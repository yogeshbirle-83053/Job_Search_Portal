from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'employer', 'industry', 'company_size', 'location', 'created_at')
    list_filter = ('industry', 'company_size', 'created_at')
    search_fields = ('company_name', 'location', 'employer__username', 'employer__email')
    ordering = ('company_name',)
