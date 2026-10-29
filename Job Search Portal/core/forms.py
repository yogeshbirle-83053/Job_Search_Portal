from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    Form for validating and saving contact messages.
    """
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John Doe',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john@example.com',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Inquiry regarding...',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'How can we help you?',
                'required': True
            }),
        }
