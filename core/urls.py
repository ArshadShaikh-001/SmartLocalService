"""
URL Configuration for Core Application
Includes Public Catalog, Customer Interactions, Auth,
Provider Dashboard, and Custom Admin Portals.
"""

from django.urls import path
from . import views

urlpatterns = [
    # --------------------------------------------------------------------------
    # Public Pages & Service Catalog
    # --------------------------------------------------------------------------
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

    # --------------------------------------------------------------------------
    # Authentication & Dashboard Redirect
    # --------------------------------------------------------------------------
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),

    # --------------------------------------------------------------------------
    # Customer Dashboard
    # --------------------------------------------------------------------------
    path('dashboard/customer/', views.customer_dashboard_view, name='customer_dashboard'),

    # --------------------------------------------------------------------------
    # Service Provider Module (/dashboard/provider/...)
    # --------------------------------------------------------------------------
    path('dashboard/provider/', views.provider_dashboard_view, name='provider_dashboard'),
    path('dashboard/provider/toggle-availability/', views.provider_toggle_availability_view, name='provider_toggle_availability'),
    path('dashboard/provider/services/', views.provider_services_view, name='provider_services'),
    path('dashboard/provider/services/add/', views.provider_service_add_view, name='provider_service_add'),
    path('dashboard/provider/services/<int:pk>/edit/', views.provider_service_edit_view, name='provider_service_edit'),
    path('dashboard/provider/services/<int:pk>/toggle-status/', views.provider_service_toggle_status_view, name='provider_service_toggle_status'),
    path('dashboard/provider/services/<int:pk>/delete/', views.provider_service_delete_view, name='provider_service_delete'),
    path('dashboard/provider/requests/', views.provider_requests_view, name='provider_requests'),
    path('dashboard/provider/requests/<int:pk>/update-status/', views.provider_request_update_status_view, name='provider_request_update_status'),
    path('dashboard/provider/enquiries/', views.provider_enquiries_view, name='provider_enquiries'),
    path('dashboard/provider/enquiries/<int:pk>/reply/', views.provider_enquiry_reply_view, name='provider_enquiry_reply'),
    path('dashboard/provider/reviews/', views.provider_reviews_view, name='provider_reviews'),

    # --------------------------------------------------------------------------
    # Custom Administrator Module (/dashboard/admin/...)
    # --------------------------------------------------------------------------
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/admin/users/', views.admin_users_view, name='admin_users'),
    path('dashboard/admin/users/<int:pk>/toggle-active/', views.admin_user_toggle_active_view, name='admin_user_toggle_active'),
    path('dashboard/admin/providers/', views.admin_providers_view, name='admin_providers'),
    path('dashboard/admin/providers/<int:pk>/toggle-verification/', views.admin_provider_toggle_verification_view, name='admin_provider_toggle_verification'),
    path('dashboard/admin/categories/', views.admin_categories_view, name='admin_categories'),
    path('dashboard/admin/categories/<int:pk>/edit/', views.admin_category_edit_view, name='admin_category_edit'),
    path('dashboard/admin/categories/<int:pk>/toggle-status/', views.admin_category_toggle_status_view, name='admin_category_toggle_status'),
    path('dashboard/admin/categories/<int:pk>/delete/', views.admin_category_delete_view, name='admin_category_delete'),
    path('dashboard/admin/services/', views.admin_services_view, name='admin_services'),
    path('dashboard/admin/services/<int:pk>/toggle-status/', views.admin_service_toggle_status_view, name='admin_service_toggle_status'),
    path('dashboard/admin/reviews/', views.admin_reviews_view, name='admin_reviews'),
    path('dashboard/admin/reviews/<int:pk>/moderate/', views.admin_review_moderate_view, name='admin_review_moderate'),
    path('dashboard/admin/requests/', views.admin_requests_view, name='admin_requests'),
    path('dashboard/admin/enquiries/', views.admin_enquiries_view, name='admin_enquiries'),
]
