from django.db import models
from django.conf import settings


class Company(models.Model):
    """
    Company model representing an organization posting jobs on the portal.
    Linked to an authenticated employer user.
    """
    INDUSTRY_CHOICES = [
        ('technology', 'Technology & IT Services'),
        ('finance', 'Banking, Financial Services & Insurance'),
        ('healthcare', 'Healthcare & Life Sciences'),
        ('education', 'Education & EdTech'),
        ('ecommerce', 'E-Commerce & Retail'),
        ('manufacturing', 'Manufacturing & Automotive'),
        ('consulting', 'Consulting & Professional Services'),
        ('media', 'Media, Advertising & Entertainment'),
        ('telecom', 'Telecommunications'),
        ('other', 'Other Industries'),
    ]

    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10 employees (Startup)'),
        ('11-50', '11-50 employees (Small)'),
        ('51-200', '51-200 employees (Mid-sized)'),
        ('201-500', '201-500 employees (Large)'),
        ('500+', '500+ employees (Enterprise)'),
    ]

    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='companies',
        help_text="The recruiter or employer who manages this company profile."
    )
    company_name = models.CharField(max_length=200, unique=True, help_text="Registered legal or brand name of the company.")
    logo = models.ImageField(
        upload_to='company_logos/',
        blank=True,
        null=True,
        help_text="Official company logo (PNG, JPG, SVG)."
    )
    description = models.TextField(help_text="Comprehensive overview of company mission, culture, and products.")
    website = models.URLField(blank=True, help_text="Company website URL (e.g. https://company.com).")
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, default='technology')
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, default='11-50')
    location = models.CharField(max_length=150, help_text="Headquarters city, state, or country (e.g. Pune, India).")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['company_name']
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.company_name

    @property
    def has_logo(self):
        return bool(self.logo and hasattr(self.logo, 'url'))

    @property
    def active_jobs_count(self):
        """Returns the number of active/published jobs for this company."""
        return self.jobs.filter(status='PUBLISHED').count()
