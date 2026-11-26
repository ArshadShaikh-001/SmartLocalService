"""
URL configuration for smart_local_service project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Customize Django Admin Header and Title for project presentation
admin.site.site_header = "Smart Local Service Connect - Admin Panel"
admin.site.site_title = "Smart Local Service Admin"
admin.site.index_title = "Platform Management Portal"
