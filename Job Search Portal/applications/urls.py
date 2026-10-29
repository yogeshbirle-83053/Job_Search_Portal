from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    # Job Seeker URLs
    path('apply/<int:job_id>/', views.apply_job_view, name='apply_job'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
    path('<int:pk>/withdraw/', views.withdraw_application_view, name='withdraw_application'),
    path('saved/', views.saved_jobs_view, name='saved_jobs'),
    path('save/<int:job_id>/', views.toggle_save_job_view, name='toggle_save_job'),

    # Employer URLs
    path('job/<int:job_id>/applicants/', views.job_applicants_view, name='job_applicants'),
    path('<int:pk>/detail/', views.applicant_detail_view, name='applicant_detail'),

    # Secure Resume Access URL
    path('<int:pk>/resume/download/', views.download_application_resume_view, name='download_resume'),
]
