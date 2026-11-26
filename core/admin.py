"""
Django Admin Configuration for Smart Local Service Connect
Registers all 7 models with customized list displays, search, and filters.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    ServiceCategory,
    ServiceProvider,
    Service,
    ServiceRequest,
    Review,
    ContactEnquiry,
)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Custom User Admin showing role, phone, and active status."""
    list_display = ('username', 'email', 'phone', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('username',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Profile Info', {
            'fields': ('role', 'phone')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Profile Info', {
            'fields': ('role', 'phone', 'email')
        }),
    )


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'area', 'experience', 'verification_status', 'availability_status')
    list_filter = ('verification_status', 'availability_status', 'area')
    search_fields = ('business_name', 'user__username', 'user__first_name', 'user__last_name', 'area', 'address')
    ordering = ('business_name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'provider', 'category', 'price_info', 'service_area', 'status')
    list_filter = ('category', 'status', 'service_area')
    search_fields = ('service_name', 'description', 'provider__business_name', 'service_area')
    ordering = ('service_name',)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'service', 'preferred_date', 'status', 'request_date')
    list_filter = ('status', 'request_date', 'preferred_date')
    search_fields = ('customer__username', 'service__service_name', 'description')
    ordering = ('-request_date',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'customer', 'rating', 'moderation_status', 'review_date')
    list_filter = ('rating', 'moderation_status', 'review_date')
    search_fields = ('customer__username', 'service__service_name', 'review_text')
    actions = ['approve_reviews', 'reject_reviews']

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(moderation_status='approved')

    @admin.action(description="Reject selected reviews")
    def reject_reviews(self, request, queryset):
        queryset.update(moderation_status='rejected')


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'customer', 'status', 'enquiry_date')
    list_filter = ('status', 'enquiry_date')
    search_fields = ('provider__business_name', 'customer__username', 'message')
    ordering = ('-enquiry_date',)
