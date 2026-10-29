from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from companies.models import Company
from jobs.models import Job
from .models import ContactMessage
from .forms import ContactForm

User = get_user_model()


def home_view(request):
    """
    Renders the public homepage featuring dynamic portal statistics,
    latest job postings, and featured hiring companies.
    """
    total_jobs = Job.objects.filter(status='PUBLISHED').count()
    total_companies = Company.objects.count()
    total_seekers = User.objects.filter(role=User.ROLE_JOB_SEEKER).count()

    latest_jobs = Job.objects.filter(
        status='PUBLISHED'
    ).select_related('company')[:6]

    featured_companies = Company.objects.all()[:4]

    return render(request, 'core/home.html', {
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'total_seekers': total_seekers,
        'latest_jobs': latest_jobs,
        'featured_companies': featured_companies,
        'categories': Job.CATEGORY_CHOICES[:8],
    })


def about_view(request):
    """
    Renders the About Us page.
    """
    return render(request, 'core/about.html')


def contact_view(request):
    """
    Renders the Contact Us page and handles incoming user inquiries.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            messages.success(
                request,
                f"Thank you, {contact_msg.name}! Your message has been received. Our team will get back to you shortly."
            )
            return redirect('core:contact')
        else:
            messages.error(request, "Please fill in all required fields accurately.")
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})


# ==========================================
# CUSTOM ERROR HANDLERS
# ==========================================

def custom_404_view(request, exception=None):
    """Custom 404 Page Not Found handler."""
    return render(request, 'errors/404.html', status=404)


def custom_403_view(request, exception=None):
    """Custom 403 Forbidden handler."""
    return render(request, 'errors/403.html', status=403)


def custom_500_view(request):
    """Custom 500 Internal Server Error handler."""
    return render(request, 'errors/500.html', status=500)
