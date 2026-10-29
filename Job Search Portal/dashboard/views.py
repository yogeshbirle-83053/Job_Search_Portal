from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import job_seeker_required, employer_required
from accounts.models import JobSeekerProfile
from companies.models import Company
from jobs.models import Job
from applications.models import JobApplication, SavedJob


@login_required
def dashboard_index_view(request):
    """
    Central dispatcher that redirects logged-in users to their
    role-specific dashboard (Seeker or Employer).
    """
    if request.user.is_employer:
        return redirect('dashboard:employer_dashboard')
    elif request.user.is_job_seeker:
        return redirect('dashboard:seeker_dashboard')
    else:
        return redirect('/admin/')


@job_seeker_required
def seeker_dashboard_view(request):
    """
    Dedicated dashboard for Job Seekers.
    Displays profile completion progress, real-time application metrics,
    recent application history, and bookmarked wishlist jobs.
    """
    profile, _ = JobSeekerProfile.objects.get_or_create(
        user=request.user,
        defaults={'full_name': request.user.get_full_name() or request.user.username}
    )

    # 1. Calculate Profile Completeness Percentage
    completion_score = 0
    if profile.full_name:
        completion_score += 10
    if profile.phone:
        completion_score += 10
    if profile.location:
        completion_score += 10
    if profile.professional_summary:
        completion_score += 15
    if profile.skills:
        completion_score += 15
    if profile.education:
        completion_score += 15
    if profile.experience:
        completion_score += 15
    if profile.has_resume:
        completion_score += 10

    # 2. Application Funnel Counts
    user_applications = JobApplication.objects.filter(applicant=request.user)
    total_applied = user_applications.count()
    under_review_count = user_applications.filter(status=JobApplication.STATUS_UNDER_REVIEW).count()
    shortlisted_count = user_applications.filter(status=JobApplication.STATUS_SHORTLISTED).count()
    hired_count = user_applications.filter(status=JobApplication.STATUS_HIRED).count()
    rejected_count = user_applications.filter(status=JobApplication.STATUS_REJECTED).count()

    # 3. Recent 5 Applications
    recent_applications = user_applications.select_related('job', 'job__company')[:5]

    # 4. Recent 4 Saved Jobs
    recent_saved_jobs = SavedJob.objects.filter(
        user=request.user
    ).select_related('job', 'job__company')[:4]

    return render(request, 'dashboard/seeker_dashboard.html', {
        'profile': profile,
        'completion_score': completion_score,
        'total_applied': total_applied,
        'under_review_count': under_review_count,
        'shortlisted_count': shortlisted_count,
        'hired_count': hired_count,
        'rejected_count': rejected_count,
        'recent_applications': recent_applications,
        'recent_saved_jobs': recent_saved_jobs,
        'total_saved': SavedJob.objects.filter(user=request.user).count(),
    })


@employer_required
def employer_dashboard_view(request):
    """
    Dedicated dashboard for Employers / Recruiters.
    Displays company branding, job metrics, applicant status breakdown,
    latest incoming candidate submissions, and active job postings.
    """
    company = Company.objects.filter(employer=request.user).first()

    # Jobs posted by this recruiter
    employer_jobs = Job.objects.filter(created_by=request.user)
    total_jobs = employer_jobs.count()
    active_jobs = employer_jobs.filter(status='PUBLISHED').count()
    closed_jobs = employer_jobs.filter(status='CLOSED').count()
    draft_jobs = employer_jobs.filter(status='DRAFT').count()

    # Applications received across all jobs of this employer
    employer_applications = JobApplication.objects.filter(
        job__created_by=request.user
    )
    total_applications = employer_applications.count()
    applied_count = employer_applications.filter(status=JobApplication.STATUS_APPLIED).count()
    under_review_count = employer_applications.filter(status=JobApplication.STATUS_UNDER_REVIEW).count()
    shortlisted_count = employer_applications.filter(status=JobApplication.STATUS_SHORTLISTED).count()
    hired_count = employer_applications.filter(status=JobApplication.STATUS_HIRED).count()
    rejected_count = employer_applications.filter(status=JobApplication.STATUS_REJECTED).count()

    # Recent 5 Incoming Applications
    recent_applications = employer_applications.select_related(
        'job',
        'applicant',
        'applicant__seeker_profile'
    )[:5]

    # Latest 5 Active Jobs
    latest_active_jobs = employer_jobs.filter(status='PUBLISHED').select_related('company')[:5]

    return render(request, 'dashboard/employer_dashboard.html', {
        'company': company,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'closed_jobs': closed_jobs,
        'draft_jobs': draft_jobs,
        'total_applications': total_applications,
        'applied_count': applied_count,
        'under_review_count': under_review_count,
        'shortlisted_count': shortlisted_count,
        'hired_count': hired_count,
        'rejected_count': rejected_count,
        'recent_applications': recent_applications,
        'latest_active_jobs': latest_active_jobs,
    })
