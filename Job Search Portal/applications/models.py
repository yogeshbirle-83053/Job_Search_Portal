import os
from django.db import models
from django.conf import settings
from accounts.validators import validate_pdf_file
from jobs.models import Job


class JobApplication(models.Model):
    """
    Represents a formal job application submitted by a Job Seeker for an opening.
    Stores a snapshot of the candidate's resume, optional cover letter, and application status.
    Guarded by database unique constraint to prevent duplicate applications.
    """
    STATUS_APPLIED = 'APPLIED'
    STATUS_UNDER_REVIEW = 'UNDER_REVIEW'
    STATUS_SHORTLISTED = 'SHORTLISTED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_HIRED = 'HIRED'

    STATUS_CHOICES = [
        (STATUS_APPLIED, 'Applied'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_SHORTLISTED, 'Shortlisted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_HIRED, 'Hired'),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="The job opening being applied for."
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="The job seeker who submitted the application."
    )
    resume = models.FileField(
        upload_to='application_resumes/',
        validators=[validate_pdf_file],
        help_text="Snapshot of the resume submitted with this specific application (PDF, Max 5MB)."
    )
    cover_letter = models.TextField(
        blank=True,
        help_text="Optional cover letter highlighting why the candidate is a strong fit."
    )
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default=STATUS_APPLIED,
        help_text="Current recruitment status of this application."
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
        constraints = [
            models.UniqueConstraint(
                fields=['job', 'applicant'],
                name='unique_job_applicant'
            )
        ]
        indexes = [
            models.Index(fields=['status', '-applied_at']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['applicant', '-applied_at']),
        ]

    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"

    @property
    def resume_filename(self):
        if self.resume:
            return os.path.basename(self.resume.name)
        return ""

    @property
    def is_withdrawable(self):
        """Candidates can withdraw an application if it is still in APPLIED or UNDER_REVIEW stage."""
        return self.status in [self.STATUS_APPLIED, self.STATUS_UNDER_REVIEW]

    @property
    def status_badge_class(self):
        """Returns Bootstrap color class corresponding to the application status."""
        mapping = {
            self.STATUS_APPLIED: 'primary',
            self.STATUS_UNDER_REVIEW: 'info',
            self.STATUS_SHORTLISTED: 'warning text-dark',
            self.STATUS_REJECTED: 'danger',
            self.STATUS_HIRED: 'success',
        }
        return mapping.get(self.status, 'secondary')


class SavedJob(models.Model):
    """
    Wishlist model allowing Job Seekers to bookmark and save jobs to revisit later.
    Guarded by database unique constraint to prevent duplicate bookmarks.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs',
        help_text="The user who bookmarked this job."
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='saved_by_users',
        help_text="The bookmarked job opening."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Saved Job'
        verbose_name_plural = 'Saved Jobs'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'job'],
                name='unique_user_saved_job'
            )
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
