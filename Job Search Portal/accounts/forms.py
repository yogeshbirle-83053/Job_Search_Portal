from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User, JobSeekerProfile
from .validators import validate_pdf_file


class UserRegistrationForm(forms.ModelForm):
    """
    Form for user registration supporting Job Seeker and Employer roles.
    Includes password confirmation, email uniqueness validation, and Bootstrap styling.
    """
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a secure password (min. 8 characters)',
            'autocomplete': 'new-password'
        }),
        help_text="Password must contain at least 8 characters."
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a unique username',
                'autocomplete': 'username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
                'autocomplete': 'email'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select',
            }, choices=[
                (User.ROLE_JOB_SEEKER, 'Job Seeker (Looking for opportunities)'),
                (User.ROLE_EMPLOYER, 'Employer / Recruiter (Hiring talent)'),
            ]),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please re-enter them carefully.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """
    Authentication form with Bootstrap 5 input classes and placeholders.
    """
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your username',
            'autofocus': True,
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Password change form styled for Bootstrap 5.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class JobSeekerProfileForm(forms.ModelForm):
    """
    Profile editing form for Job Seekers.
    Includes profile image, PDF resume, skills, education, and experience.
    """
    class Meta:
        model = JobSeekerProfile
        fields = [
            'full_name',
            'phone',
            'location',
            'professional_summary',
            'skills',
            'education',
            'experience',
            'resume',
            'profile_picture',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Johnathan Doe'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +91 9876543210'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bengaluru, Karnataka, India'}),
            'professional_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Briefly describe your career background, core strengths, and goals...'
            }),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Python, Django, MySQL, REST APIs, JavaScript, Git'
            }),
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g. B.Tech in Computer Science, XYZ University (2020 - 2024) - CGPA 8.5'
            }),
            'experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'e.g. Software Developer Intern at ABC Tech (6 Months): Built REST APIs and MySQL queries...'
            }),
            'resume': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class ResumeUploadForm(forms.ModelForm):
    """
    Dedicated quick-upload form for updating resume in PDF format.
    """
    class Meta:
        model = JobSeekerProfile
        fields = ['resume']
        widgets = {
            'resume': forms.FileInput(attrs={'class': 'form-control form-control-lg', 'accept': '.pdf'})
        }
