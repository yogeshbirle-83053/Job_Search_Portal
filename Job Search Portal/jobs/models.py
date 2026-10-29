from django.db import models
from django.conf import settings
from django.utils import timezone
from companies.models import Company


class Job(models.Model):
    """
    Job model representing a job opening posted by an employer.
    Contains detailed job specifications, compensation, requirements, and status.
    """
    CATEGORY_CHOICES = [
        ('software', 'Software & Web Development'),
        ('data_ai', 'Data Science & Artificial Intelligence'),
        ('devops_cloud', 'DevOps, Cloud & Infrastructure'),
        ('cybersecurity', 'Cybersecurity & InfoSec'),
        ('design', 'UI/UX & Graphic Design'),
        ('marketing', 'Digital Marketing & Content'),
        ('sales_business', 'Sales & Business Development'),
        ('finance_accounting', 'Finance & Accounting'),
        ('human_resources', 'Human Resources & Talent Acquisition'),
        ('customer_support', 'Customer Support & Operations'),
        ('product_management', 'Product & Project Management'),
        ('other', 'Other Specializations'),
    ]

    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
        ('remote', 'Remote'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('fresher', 'Fresher (0 years)'),
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (2-5 years)'),
        ('senior', 'Senior Level (5+ years)'),
    ]

    STATUS_CHOICES = [
        ('PUBLISHED', 'Published / Active'),
        ('DRAFT', 'Draft'),
        ('CLOSED', 'Closed'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text="The company offering this position."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs',
        help_text="The employer / recruiter who posted this job opening."
    )
    title = models.CharField(max_length=200, help_text="e.g. Senior Full Stack Django Developer")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='software')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='entry')
    location = models.CharField(max_length=150, help_text="e.g. Bengaluru, India (or 'Remote')")
    
    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum annual salary in INR (e.g. 500000.00)"
    )
    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum annual salary in INR (e.g. 900000.00)"
    )
    
    application_deadline = models.DateField(
        null=True,
        blank=True,
        help_text="Last date for candidates to submit applications."
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PUBLISHED')
    
    description = models.TextField(help_text="Overview of the position, team mission, and opportunity.")
    responsibilities = models.TextField(
        blank=True,
        help_text="Day-to-day duties, engineering tasks, and expected deliverables."
    )
    required_skills = models.TextField(
        help_text="Comma-separated required skills and competencies (e.g. Python, Django, MySQL, REST APIs)."
    )
    views_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['job_type']),
            models.Index(fields=['experience_level']),
        ]

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"

    @property
    def is_open(self):
        """Returns True if the job is published and not expired."""
        if self.status != 'PUBLISHED':
            return False
        if self.application_deadline and self.application_deadline < timezone.now().date():
            return False
        return True

    def get_skills_list(self):
        """Returns required skills as a clean list of trimmed strings."""
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    @property
    def formatted_salary(self):
        """Returns a user-friendly formatted salary string."""
        if self.salary_min and self.salary_max:
            return f"₹{self.salary_min:,.0f} - ₹{self.salary_max:,.0f} / year"
        elif self.salary_min:
            return f"From ₹{self.salary_min:,.0f} / year"
        elif self.salary_max:
            return f"Up to ₹{self.salary_max:,.0f} / year"
        return "Competitive / Negotiable"

    @property
    def total_applicants(self):
        """Returns total applications submitted for this job."""
        return self.applications.count() if hasattr(self, 'applications') else 0
