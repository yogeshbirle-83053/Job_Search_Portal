import os
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .validators import validate_pdf_file


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds role-based authorization for Job Seekers, Employers, and Admins.
    """
    ROLE_JOB_SEEKER = 'job_seeker'
    ROLE_EMPLOYER = 'employer'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_JOB_SEEKER, 'Job Seeker'),
        (ROLE_EMPLOYER, 'Employer'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    email = models.EmailField(unique=True, help_text="Required. Must be a valid and unique email address.")
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_JOB_SEEKER,
        help_text="Specifies the user's role on the portal."
    )

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_job_seeker(self):
        return self.role == self.ROLE_JOB_SEEKER

    @property
    def is_employer(self):
        return self.role == self.ROLE_EMPLOYER

    @property
    def is_portal_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser


class JobSeekerProfile(models.Model):
    """
    Extended profile for Job Seekers containing professional details, resume, and skills.
    One-to-One relationship with the User model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='seeker_profile'
    )
    full_name = models.CharField(max_length=150, blank=True, help_text="Your legal full name.")
    phone = models.CharField(max_length=20, blank=True, help_text="Contact telephone / WhatsApp number.")
    location = models.CharField(max_length=150, blank=True, help_text="City, State / Country (e.g., Bengaluru, India).")
    professional_summary = models.TextField(
        blank=True,
        help_text="Brief professional summary, career objective, or pitch."
    )
    skills = models.TextField(
        blank=True,
        help_text="Comma-separated skills (e.g., Python, Django, MySQL, JavaScript, Git)."
    )
    education = models.TextField(
        blank=True,
        help_text="Highest qualification, degree, college/university, and graduation year."
    )
    experience = models.TextField(
        blank=True,
        help_text="Work history, internships, key projects, and responsibilities."
    )
    resume = models.FileField(
        upload_to='resumes/',
        validators=[validate_pdf_file],
        blank=True,
        null=True,
        help_text="Upload your resume in PDF format only (Max 5MB)."
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text="Professional avatar or headshot image."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Job Seeker Profile'
        verbose_name_plural = 'Job Seeker Profiles'

    def __str__(self):
        return f"{self.full_name or self.user.username}'s Profile"

    @property
    def has_resume(self):
        return bool(self.resume and hasattr(self.resume, 'url'))

    @property
    def resume_filename(self):
        if self.resume:
            return os.path.basename(self.resume.name)
        return ""

    def get_skills_list(self):
        """Returns skills as a clean list of trimmed strings."""
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]


@receiver(post_save, sender=User)
def create_or_update_seeker_profile(sender, instance, created, **kwargs):
    """
    Signal receiver: Automatically creates a JobSeekerProfile when a new
    user registers with the 'job_seeker' role.
    """
    if created and instance.role == User.ROLE_JOB_SEEKER:
        JobSeekerProfile.objects.get_or_create(
            user=instance,
            defaults={'full_name': instance.get_full_name() or instance.username}
        )
