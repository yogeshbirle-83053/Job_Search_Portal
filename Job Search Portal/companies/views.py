from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import employer_required
from .models import Company
from .forms import CompanyForm


def company_list_view(request):
    """
    Public directory of registered companies.
    Supports search by keyword and filtering by industry with pagination.
    """
    query = request.GET.get('q', '').strip()
    industry_filter = request.GET.get('industry', '').strip()

    companies = Company.objects.all()

    if query:
        companies = companies.filter(
            Q(company_name__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )

    if industry_filter:
        companies = companies.filter(industry=industry_filter)

    paginator = Paginator(companies, 9)  # 9 companies per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'companies/company_list.html', {
        'page_obj': page_obj,
        'query': query,
        'industry_filter': industry_filter,
        'industries': Company.INDUSTRY_CHOICES,
        'total_companies': companies.count(),
    })


def company_detail_view(request, pk):
    """
    Public view of a specific company with full overview and open positions.
    """
    company = get_object_or_404(Company, pk=pk)
    # Open jobs will be accessible via company.jobs.filter(status='PUBLISHED')
    open_jobs = company.jobs.filter(status='PUBLISHED') if hasattr(company, 'jobs') else []

    return render(request, 'companies/company_detail.html', {
        'company': company,
        'open_jobs': open_jobs,
    })


@employer_required
def my_company_view(request):
    """
    Displays the authenticated Employer's company profile.
    If no company exists yet, prompts them to create one.
    """
    company = request.user.companies.first()
    return render(request, 'companies/my_company.html', {
        'company': company
    })


@employer_required
def create_company_view(request):
    """
    Enables an Employer to create a new company profile.
    """
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.employer = request.user
            company.save()
            messages.success(request, f"Company profile '{company.company_name}' created successfully!")
            return redirect('companies:my_company')
        else:
            messages.error(request, "Please fix the validation errors below.")
    else:
        form = CompanyForm()

    return render(request, 'companies/company_form.html', {
        'form': form,
        'title': 'Create Company Profile'
    })


@employer_required
def edit_company_view(request, pk):
    """
    Enables an Employer to edit their own company profile.
    Strictly verifies ownership: employer=request.user (IDOR protection).
    """
    company = get_object_or_404(Company, pk=pk, employer=request.user)

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Company details updated successfully!")
            return redirect('companies:my_company')
        else:
            messages.error(request, "Please fix the validation errors below.")
    else:
        form = CompanyForm(instance=company)

    return render(request, 'companies/company_form.html', {
        'form': form,
        'company': company,
        'title': f"Edit {company.company_name}"
    })
