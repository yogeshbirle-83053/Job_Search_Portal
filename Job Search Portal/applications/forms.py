from django import forms
from django.core.exceptions import ValidationError
from accounts.validators import validate_pdf_file
from .models import JobApplication


class JobApplicationForm(forms.Form):
    """
    Form for Job Seekers to apply for an active job opening.
    Allows candidate to use their existing profile resume or upload a tailored resume.
    """
    RESUME_CHOICES = [
        ('profile', 'Use my existing profile resume'),
        ('upload', 'Upload a tailored resume for this job'),
    ]

    resume_choice = forms.ChoiceField(
        choices=RESUME_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='profile',
        label="Select Resume Option"
    )
    custom_resume = forms.FileField(
        required=False,
        validators=[validate_pdf_file],
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        label="Upload Custom Resume (PDF only, Max 5MB)"
    )
    cover_letter = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Explain why your skills, experience, and passions make you an ideal match for this opening...'
        }),
        label="Cover Letter (Optional)"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.job = kwargs.pop('job', None)
        super().__init__(*args, **kwargs)

        # If user does not have a profile resume, default choice to 'upload'
        has_profile_resume = False
        if self.user and hasattr(self.user, 'seeker_profile'):
            has_profile_resume = self.user.seeker_profile.has_resume

        if not has_profile_resume:
            self.fields['resume_choice'].initial = 'upload'

    def clean(self):
        cleaned_data = super().clean()
        resume_choice = cleaned_data.get('resume_choice')
        custom_resume = cleaned_data.get('custom_resume')

        # 1. Verify user hasn't already applied
        if self.user and self.job:
            if JobApplication.objects.filter(job=self.job, applicant=self.user).exists():
                raise ValidationError("You have already submitted an application for this job opening.")

        # 2. Verify job is currently active
        if self.job and not self.job.is_open:
            raise ValidationError("This job opening is closed and is no longer accepting applications.")

        # 3. Validate resume selection
        if resume_choice == 'profile':
            if not self.user or not hasattr(self.user, 'seeker_profile') or not self.user.seeker_profile.has_resume:
                self.add_error(
                    'resume_choice',
                    "You do not have a resume uploaded to your profile yet. Please choose 'Upload a tailored resume' below."
                )
        elif resume_choice == 'upload':
            if not custom_resume:
                self.add_error(
                    'custom_resume',
                    "Please select and upload a PDF resume file."
                )

        return cleaned_data


class ApplicationStatusUpdateForm(forms.ModelForm):
    """
    Form for Employers to transition applicant status (Applied -> Review -> Shortlist/Reject/Hire).
    """
    class Meta:
        model = JobApplication
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }
