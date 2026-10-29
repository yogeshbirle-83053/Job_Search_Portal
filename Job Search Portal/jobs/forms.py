from django import forms
from django.utils import timezone
from .models import Job
from companies.models import Company


class JobPostForm(forms.ModelForm):
    """
    Form for Employers to create and update job openings.
    Ensures that only companies owned by the requesting employer can be selected.
    """
    class Meta:
        model = Job
        fields = [
            'title',
            'company',
            'category',
            'job_type',
            'experience_level',
            'location',
            'salary_min',
            'salary_max',
            'application_deadline',
            'status',
            'description',
            'responsibilities',
            'required_skills',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. Senior Full Stack Django Developer'
            }),
            'company': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Bengaluru, India or Remote'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Min (₹ INR, e.g. 600000)'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Max (₹ INR, e.g. 1000000)'
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Comprehensive role description, team mission, and impact...'
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Bullet points of core responsibilities and deliverables...'
            }),
            'required_skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comma-separated skills (e.g. Python, Django, MySQL, REST APIs, Git)'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Allow passing the current user so we can restrict the company dropdown
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            user_companies = Company.objects.filter(employer=user)
            self.fields['company'].queryset = user_companies
            if user_companies.count() == 1:
                self.fields['company'].initial = user_companies.first()

    def clean_application_deadline(self):
        deadline = self.cleaned_data.get('application_deadline')
        if deadline and deadline < timezone.now().date():
            raise forms.ValidationError("Application deadline cannot be in the past.")
        return deadline

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')

        if salary_min and salary_max and salary_max < salary_min:
            self.add_error('salary_max', "Maximum salary cannot be less than minimum salary.")

        return cleaned_data
