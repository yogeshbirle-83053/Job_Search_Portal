from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.role_redirect_view, name='role_redirect'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('profile/', views.seeker_profile_view, name='seeker_profile'),
    path('profile/edit/', views.edit_seeker_profile_view, name='edit_profile'),
    path('profile/resume/', views.upload_resume_view, name='upload_resume'),
]
