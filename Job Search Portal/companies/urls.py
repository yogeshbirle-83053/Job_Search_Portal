from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('', views.company_list_view, name='company_list'),
    path('profile/', views.my_company_view, name='my_company'),
    path('create/', views.create_company_view, name='create_company'),
    path('<int:pk>/', views.company_detail_view, name='company_detail'),
    path('<int:pk>/edit/', views.edit_company_view, name='edit_company'),
]
