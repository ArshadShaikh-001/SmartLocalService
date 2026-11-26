"""
URL Configuration for Core Application
Includes Public Catalog, Customer Interactions, Auth, and Dashboards.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Public Pages & Service Catalog
    path('', views.home_view, name='home'),
    path('categories/', views.categories_view, name='categories'),
    path('services/', views.services_view, name='services'),
    path('services/<int:pk>/', views.service_detail_view, name='service_detail'),
    path('services/<int:pk>/request/', views.service_request_create_view, name='service_request_create'),
    path('services/<int:pk>/enquiry/', views.service_enquiry_create_view, name='service_enquiry_create'),
    path('services/<int:pk>/review/', views.review_create_view, name='review_create'),

    # Provider Profiles & Direct Enquiries
    path('providers/<int:pk>/', views.provider_profile_view, name='provider_profile'),
    path('providers/<int:pk>/enquiry/', views.provider_enquiry_create_view, name='provider_enquiry_create'),

    # Customer Request Cancellation
    path('requests/<int:pk>/cancel/', views.cancel_request_view, name='cancel_request'),

    # Static Informational Pages
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards & Redirection
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),
    path('dashboard/customer/', views.customer_dashboard_view, name='customer_dashboard'),
    path('dashboard/provider/', views.provider_dashboard_view, name='provider_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
]
