from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index_view, name='index'),
    path('seeker/', views.seeker_dashboard_view, name='seeker_dashboard'),
    path('employer/', views.employer_dashboard_view, name='employer_dashboard'),
]
