from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from django.http import FileResponse, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from accounts.decorators import job_seeker_required, employer_required
from jobs.models import Job
from .models import JobApplication, SavedJob
from .forms import JobApplicationForm, ApplicationStatusUpdateForm


# ==========================================
# JOB SEEKER APPLICATION WORKFLOWS
# ==========================================

@job_seeker_required
def apply_job_view(request, job_id):
    """
    Handles job application submission for a specific opening.
    Verifies authentication, job seeker role, open job status, and duplicate submission.
    Allows candidate to use existing profile resume or upload a tailored resume.
    """
    job = get_object_or_404(Job.objects.select_related('company'), pk=job_id)

    # 1. Guard: check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already submitted an application for this position.")
        return redirect('jobs:job_detail', pk=job.pk)

    # 2. Guard: check if job is still active
    if not job.is_open:
        messages.error(request, "This job opening is closed and is no longer accepting new applications.")
        return redirect('jobs:job_detail', pk=job.pk)

    profile = getattr(request.user, 'seeker_profile', None)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES, user=request.user, job=job)
        if form.is_valid():
            resume_choice = form.cleaned_data['resume_choice']
            cover_letter = form.cleaned_data.get('cover_letter', '')

            application = JobApplication(
                job=job,
                applicant=request.user,
                cover_letter=cover_letter,
                status=JobApplication.STATUS_APPLIED
            )

            # Assign resume snapshot
            if resume_choice == 'profile' and profile and profile.has_resume:
                # Read profile resume bytes and save as a snapshot to prevent future profile edits from altering submitted resume
                profile.resume.open('rb')
                content = profile.resume.read()
                filename = f"app_{request.user.username}_{job.pk}.pdf"
                application.resume.save(filename, ContentFile(content), save=False)
            else:
                application.resume = form.cleaned_data['custom_resume']

            application.save()
            messages.success(
                request,
                f"Application submitted successfully for '{job.title}'! You can track its progress below."
            )
            return redirect('applications:my_applications')
        else:
            messages.error(request, "Please resolve the errors highlighted below to submit your application.")
    else:
        form = JobApplicationForm(user=request.user, job=job)

    return render(request, 'applications/apply_job.html', {
        'job': job,
        'form': form,
        'profile': profile,
    })


@job_seeker_required
def my_applications_view(request):
    """
    Displays the Job Seeker's complete application history,
    current review statuses, and withdrawal capabilities.
    """
    status_filter = request.GET.get('status', 'ALL')
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__company')

    if status_filter != 'ALL':
        applications = applications.filter(status=status_filter)

    # Metrics
    total_count = JobApplication.objects.filter(applicant=request.user).count()
    under_review_count = JobApplication.objects.filter(applicant=request.user, status=JobApplication.STATUS_UNDER_REVIEW).count()
    shortlisted_count = JobApplication.objects.filter(applicant=request.user, status=JobApplication.STATUS_SHORTLISTED).count()
    hired_count = JobApplication.objects.filter(applicant=request.user, status=JobApplication.STATUS_HIRED).count()

    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'applications/my_applications.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_count': total_count,
        'under_review_count': under_review_count,
        'shortlisted_count': shortlisted_count,
        'hired_count': hired_count,
    })


@job_seeker_required
def withdraw_application_view(request, pk):
    """
    Allows a Job Seeker to withdraw their application if it is still eligible (APPLIED or UNDER_REVIEW).
    IDOR protected: verifies applicant=request.user.
    """
    application = get_object_or_404(JobApplication, pk=pk, applicant=request.user)
    job_title = application.job.title

    if not application.is_withdrawable:
        messages.error(
            request,
            f"Your application for '{job_title}' has already progressed to the '{application.get_status_display()}' stage and cannot be withdrawn."
        )
        return redirect('applications:my_applications')

    application.delete()
    messages.info(request, f"Your application for '{job_title}' has been successfully withdrawn.")
    return redirect('applications:my_applications')


@job_seeker_required
def saved_jobs_view(request):
    """
    Displays all positions saved to the candidate's wishlist.
    """
    saved_records = SavedJob.objects.filter(
        user=request.user
    ).select_related('job', 'job__company')

    paginator = Paginator(saved_records, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'applications/saved_jobs.html', {
        'page_obj': page_obj,
        'total_saved': saved_records.count(),
    })


@job_seeker_required
def toggle_save_job_view(request, job_id):
    """
    Toggles a job in the authenticated candidate's saved wishlist.
    """
    job = get_object_or_404(Job, pk=job_id)
    saved_item = SavedJob.objects.filter(user=request.user, job=job).first()

    if saved_item:
        saved_item.delete()
        messages.info(request, f"Removed '{job.title}' from your saved wishlist.")
    else:
        SavedJob.objects.create(user=request.user, job=job)
        messages.success(request, f"Added '{job.title}' to your saved wishlist!")

    referer = request.META.get('HTTP_REFERER')
    if referer and ('/jobs/' in referer or '/saved/' in referer):
        return redirect(referer)
    return redirect('jobs:job_detail', pk=job.pk)


# ==========================================
# EMPLOYER APPLICANT MANAGEMENT WORKFLOWS
# ==========================================

@employer_required
def job_applicants_view(request, job_id):
    """
    Recruiter dashboard listing all candidates who applied for a specific job opening.
    IDOR protected: verifies job__created_by=request.user.
    """
    job = get_object_or_404(Job, pk=job_id, created_by=request.user)
    status_filter = request.GET.get('status', 'ALL')

    applicants_qs = JobApplication.objects.filter(
        job=job
    ).select_related('applicant', 'applicant__seeker_profile')

    if status_filter != 'ALL':
        applicants_qs = applicants_qs.filter(status=status_filter)

    total_applied = job.applications.count()
    shortlisted = job.applications.filter(status=JobApplication.STATUS_SHORTLISTED).count()
    hired = job.applications.filter(status=JobApplication.STATUS_HIRED).count()

    paginator = Paginator(applicants_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'applications/job_applicants.html', {
        'job': job,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_applied': total_applied,
        'shortlisted': shortlisted,
        'hired': hired,
        'status_choices': JobApplication.STATUS_CHOICES,
    })


@employer_required
def applicant_detail_view(request, pk):
    """
    Detailed candidate evaluation view for recruiters.
    Displays applicant's bio, skills, experience, education, submitted resume,
    cover letter, and an inline form to transition recruitment status.
    IDOR protected: verifies job__created_by=request.user.
    """
    application = get_object_or_404(
        JobApplication.objects.select_related(
            'job',
            'job__company',
            'applicant',
            'applicant__seeker_profile'
        ),
        pk=pk,
        job__created_by=request.user
    )

    if request.method == 'POST':
        status_form = ApplicationStatusUpdateForm(request.POST, instance=application)
        if status_form.is_valid():
            status_form.save()
            messages.success(
                request,
                f"Applicant status successfully updated to '{application.get_status_display()}'."
            )
            return redirect('applications:applicant_detail', pk=application.pk)
    else:
        status_form = ApplicationStatusUpdateForm(instance=application)

    profile = getattr(application.applicant, 'seeker_profile', None)

    return render(request, 'applications/applicant_detail.html', {
        'application': application,
        'profile': profile,
        'skills_list': profile.get_skills_list() if profile else [],
        'status_form': status_form,
    })


@login_required
def download_application_resume_view(request, pk):
    """
    Secure endpoint for streaming candidate resumes.
    Strictly verifies authorization: only the candidate who submitted it,
    the recruiter who posted the job, or an administrator can access it.
    Prevents unauthorized public scraping of candidate resumes.
    """
    application = get_object_or_404(
        JobApplication.objects.select_related('job'),
        pk=pk
    )

    if (request.user != application.applicant and 
        request.user != application.job.created_by and 
        not request.user.is_superuser):
        raise PermissionDenied("You are not authorized to view or download this candidate's resume.")

    if not application.resume:
        raise Http404("Resume file not found.")

    response = FileResponse(application.resume.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{application.resume_filename}"'
    return response
