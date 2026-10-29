from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list_view, name='job_list'),
    path('post/', views.create_job_view, name='create_job'),
    path('manage/', views.manage_jobs_view, name='manage_jobs'),
    path('<int:pk>/', views.job_detail_view, name='job_detail'),
    path('<int:pk>/edit/', views.edit_job_view, name='edit_job'),
    path('<int:pk>/delete/', views.delete_job_view, name='delete_job'),
    path('<int:pk>/toggle-status/', views.toggle_job_status_view, name='toggle_status'),
]
