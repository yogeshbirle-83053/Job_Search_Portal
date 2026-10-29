from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    CustomPasswordChangeForm,
    JobSeekerProfileForm,
    ResumeUploadForm
)
from .models import User, JobSeekerProfile
from .decorators import job_seeker_required, employer_required


def register_view(request):
    """
    Handles user registration with role selection (Job Seeker or Employer).
    Validates unique email and strong passwords, then redirects to login upon success.
    """
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role_display = user.get_role_display()
            messages.success(
                request,
                f"Account created successfully as a {role_display}! Please sign in below to continue."
            )
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors indicated below to complete registration.")
    else:
        initial_role = request.GET.get('role', User.ROLE_JOB_SEEKER)
        if initial_role not in [User.ROLE_JOB_SEEKER, User.ROLE_EMPLOYER]:
            initial_role = User.ROLE_JOB_SEEKER
        form = UserRegistrationForm(initial={'role': initial_role})

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handles user authentication. On successful authentication, creates session
    and redirects user to their intended destination or role dashboard.
    """
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # Safe redirect: check 'next' parameter
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('accounts:role_redirect')
        else:
            messages.error(request, "Invalid username or password. Please verify your credentials and try again.")
    else:
        form = UserLoginForm(request)

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })


def logout_view(request):
    """
    Logs out the current user, flushes session data, and redirects to login.
    """
    logout(request)
    messages.info(request, "You have been safely logged out. See you next time!")
    return redirect('accounts:login')


@login_required
def role_redirect_view(request):
    """
    Central dispatcher that inspects the authenticated user's role
    and redirects them to their specialized dashboard.
    """
    if request.user.is_employer:
        return redirect('dashboard:employer_dashboard')
    elif request.user.is_job_seeker:
        return redirect('dashboard:seeker_dashboard')
    else:
        return redirect('/admin/')


@login_required
def change_password_view(request):
    """
    Allows authenticated users to change their account password.
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully!")
            return redirect('accounts:role_redirect')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


# ==========================================
# JOB SEEKER PROFILE VIEWS
# ==========================================

@job_seeker_required
def seeker_profile_view(request):
    """
    Displays the Job Seeker's complete professional profile,
    uploaded resume preview/download, and formatted skills list.
    """
    profile, _ = JobSeekerProfile.objects.get_or_create(
        user=request.user,
        defaults={'full_name': request.user.get_full_name() or request.user.username}
    )
    return render(request, 'accounts/seeker_profile.html', {
        'profile': profile,
        'skills_list': profile.get_skills_list()
    })


@job_seeker_required
def edit_seeker_profile_view(request):
    """
    Enables Job Seekers to update their personal info, bio, skills, education,
    experience, profile picture, and PDF resume.
    """
    profile, _ = JobSeekerProfile.objects.get_or_create(
        user=request.user,
        defaults={'full_name': request.user.get_full_name() or request.user.username}
    )

    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:seeker_profile')
        else:
            messages.error(request, "Please fix the validation errors in the form below.")
    else:
        form = JobSeekerProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'profile': profile
    })


@job_seeker_required
def upload_resume_view(request):
    """
    Dedicated view for fast resume upload and replacement.
    Validates PDF format and max 5MB size.
    """
    profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Resume uploaded and saved successfully!")
            return redirect('accounts:seeker_profile')
        else:
            messages.error(request, "Invalid resume file. Please upload a valid PDF file under 5MB.")
    else:
        form = ResumeUploadForm(instance=profile)

    return render(request, 'accounts/upload_resume.html', {
        'form': form,
        'profile': profile
    })
