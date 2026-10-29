"""
URL configuration for Job Search Portal project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('companies/', include('companies.urls', namespace='companies')),
    path('applications/', include('applications.urls', namespace='applications')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]

# Serve user-uploaded media files and static files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Error Handlers
handler404 = 'core.views.custom_404_view'
handler403 = 'core.views.custom_403_view'
handler500 = 'core.views.custom_500_view'
