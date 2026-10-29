from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.utils import timezone
from accounts.decorators import employer_required
from companies.models import Company
from .models import Job
from .forms import JobPostForm


def job_list_view(request):
    """
    Public searchable & filterable directory of published job openings.
    Supports search across title, description, skills, and company name,
    along with category, job type, experience level, location, and salary filtering.
    """
    # Query parameters
    query = request.GET.get('q', '').strip()
    location_filter = request.GET.get('location', '').strip()
    category_filter = request.GET.get('category', '').strip()
    job_type_filter = request.GET.get('job_type', '').strip()
    exp_filter = request.GET.get('experience_level', '').strip()
    min_salary = request.GET.get('min_salary', '').strip()
    sort_by = request.GET.get('sort_by', 'newest')

    # Base queryset: only published jobs with active or unexpired deadlines
    today = timezone.now().date()
    jobs = Job.objects.filter(
        status='PUBLISHED'
    ).filter(
        Q(application_deadline__gte=today) | Q(application_deadline__isnull=True)
    ).select_related('company')

    # Apply search keyword
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(required_skills__icontains=query) |
            Q(company__company_name__icontains=query)
        )

    # Apply location filter
    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)

    # Apply category filter
    if category_filter:
        jobs = jobs.filter(category=category_filter)

    # Apply job type filter
    if job_type_filter:
        jobs = jobs.filter(job_type=job_type_filter)

    # Apply experience level filter
    if exp_filter:
        jobs = jobs.filter(experience_level=exp_filter)

    # Apply minimum salary filter
    if min_salary:
        try:
            min_salary_val = float(min_salary)
            jobs = jobs.filter(
                Q(salary_max__gte=min_salary_val) | Q(salary_min__gte=min_salary_val)
            )
        except ValueError:
            pass

    # Ordering
    if sort_by == 'salary_high':
        jobs = jobs.order_by('-salary_max', '-created_at')
    elif sort_by == 'popular':
        jobs = jobs.order_by('-views_count', '-created_at')
    else:
        jobs = jobs.order_by('-created_at')

    # Pagination: 10 jobs per page
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Popular categories count for sidebar/quick links
    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'query': query,
        'location_filter': location_filter,
        'category_filter': category_filter,
        'job_type_filter': job_type_filter,
        'exp_filter': exp_filter,
        'min_salary': min_salary,
        'sort_by': sort_by,
        'categories': Job.CATEGORY_CHOICES,
        'job_types': Job.JOB_TYPE_CHOICES,
        'experience_levels': Job.EXPERIENCE_LEVEL_CHOICES,
        'total_jobs_count': jobs.count(),
    })


def job_detail_view(request, pk):
    """
    Displays full details of a single job opening.
    Increments views count and suggests similar roles.
    """
    job = get_object_or_404(Job.objects.select_related('company'), pk=pk)

    # Permission check for unpublished jobs: only owner or admin can preview
    if job.status != 'PUBLISHED':
        if not request.user.is_authenticated or (request.user != job.created_by and not request.user.is_superuser):
            messages.error(request, "This job posting is currently not active or available to the public.")
            return redirect('jobs:job_list')

    # Increment view count safely
    Job.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
    job.refresh_from_db(fields=['views_count'])

    # Check application and saved status for authenticated job seeker
    has_applied = False
    is_saved = False
    if request.user.is_authenticated and request.user.is_job_seeker:
        if hasattr(job, 'applications'):
            has_applied = job.applications.filter(applicant=request.user).exists()
        if hasattr(request.user, 'saved_jobs'):
            is_saved = request.user.saved_jobs.filter(job=job).exists()

    # Similar jobs in same category
    similar_jobs = Job.objects.filter(
        category=job.category,
        status='PUBLISHED'
    ).exclude(pk=job.pk)[:3]

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'skills_list': job.get_skills_list(),
        'has_applied': has_applied,
        'is_saved': is_saved,
        'similar_jobs': similar_jobs,
    })


@employer_required
def create_job_view(request):
    """
    Enables an employer to post a new job opening.
    Verifies they have created at least one company first.
    """
    user_companies = Company.objects.filter(employer=request.user)
    if not user_companies.exists():
        messages.warning(
            request,
            "You must create a Company Profile before posting job openings. Please set up your company details first."
        )
        return redirect('companies:create_company')

    if request.method == 'POST':
        form = JobPostForm(request.POST, user=request.user)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            messages.success(request, f"Job posting '{job.title}' created and published successfully!")
            return redirect('jobs:manage_jobs')
        else:
            messages.error(request, "Please correct the form errors indicated below.")
    else:
        form = JobPostForm(user=request.user)

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'title': 'Post a New Job Opening'
    })


@employer_required
def manage_jobs_view(request):
    """
    Recruiter dashboard table listing all jobs posted by the authenticated employer.
    Supports filtering by status (All, Published, Draft, Closed).
    """
    status_filter = request.GET.get('status', 'ALL')
    jobs = Job.objects.filter(created_by=request.user).select_related('company')

    if status_filter != 'ALL':
        jobs = jobs.filter(status=status_filter)

    total_jobs = Job.objects.filter(created_by=request.user).count()
    active_jobs = Job.objects.filter(created_by=request.user, status='PUBLISHED').count()
    closed_jobs = Job.objects.filter(created_by=request.user, status='CLOSED').count()
    draft_jobs = Job.objects.filter(created_by=request.user, status='DRAFT').count()

    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/manage_jobs.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'closed_jobs': closed_jobs,
        'draft_jobs': draft_jobs,
    })


@employer_required
def edit_job_view(request, pk):
    """
    Allows recruiter to edit their own job posting.
    IDOR protected: verifies created_by=request.user.
    """
    job = get_object_or_404(Job, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job '{job.title}' updated successfully!")
            return redirect('jobs:manage_jobs')
        else:
            messages.error(request, "Please fix the errors indicated below.")
    else:
        form = JobPostForm(instance=job, user=request.user)

    return render(request, 'jobs/job_form.html', {
        'form': form,
        'job': job,
        'title': f"Edit Job: {job.title}"
    })


@employer_required
def delete_job_view(request, pk):
    """
    Allows recruiter to permanently delete their job opening.
    IDOR protected: verifies created_by=request.user.
    """
    job = get_object_or_404(Job, pk=pk, created_by=request.user)
    job_title = job.title
    job.delete()
    messages.success(request, f"Job posting '{job_title}' was successfully deleted.")
    return redirect('jobs:manage_jobs')


@employer_required
def toggle_job_status_view(request, pk):
    """
    Quick action to toggle a job between PUBLISHED and CLOSED.
    IDOR protected: verifies created_by=request.user.
    """
    job = get_object_or_404(Job, pk=pk, created_by=request.user)
    if job.status == 'PUBLISHED':
        job.status = 'CLOSED'
        messages.info(request, f"Job '{job.title}' has been closed for new applications.")
    else:
        job.status = 'PUBLISHED'
        messages.success(request, f"Job '{job.title}' is now published and accepting applications.")
    job.save()
    return redirect('jobs:manage_jobs')
