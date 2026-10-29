from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def job_seeker_required(view_func):
    """
    Decorator for views that checks that the user is logged in and has the Job Seeker role.
    Redirects employers to their employer dashboard with an explanatory warning message.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_job_seeker or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.warning(
            request,
            "Access restricted: This section is exclusively for Job Seekers. You have been redirected to your Employer Dashboard."
        )
        return redirect('dashboard:employer_dashboard')
    return _wrapped_view


def employer_required(view_func):
    """
    Decorator for views that checks that the user is logged in and has the Employer role.
    Redirects job seekers to their job seeker dashboard with an explanatory warning message.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_employer or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.warning(
            request,
            "Access restricted: This section is exclusively for Employers. You have been redirected to your Job Seeker Dashboard."
        )
        return redirect('dashboard:seeker_dashboard')
    return _wrapped_view


def admin_required(view_func):
    """
    Decorator for views restricted to portal administrators / superusers.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_portal_admin:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied("You do not have administrative permissions to access this page.")
    return _wrapped_view
