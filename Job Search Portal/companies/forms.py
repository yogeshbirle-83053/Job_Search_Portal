from django import forms
from .models import Company


class CompanyForm(forms.ModelForm):
    """
    Form for Employers to create and update their company profile.
    """
    class Meta:
        model = Company
        fields = [
            'company_name',
            'logo',
            'industry',
            'company_size',
            'website',
            'location',
            'description',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g. Innovatech Solutions Pvt Ltd'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'industry': forms.Select(attrs={
                'class': 'form-select'
            }),
            'company_size': forms.Select(attrs={
                'class': 'form-select'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.example.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Hyderabad, Telangana, India'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your company, what you do, work culture, and key perks...'
            }),
        }
