"""
Core Database Models for Smart Local Service Connect
Platform: Finding Trusted Local Services (BCA Mini Project)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


# ==============================================================================
# 1. Custom User Model
# Extends Django's AbstractUser to include role-based access & phone number.
# Status is handled cleanly using Django's built-in `is_active` attribute.
# ==============================================================================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
        ('admin', 'Admin'),
    )

    phone = models.CharField(max_length=15, blank=True, help_text="Contact phone number")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def is_customer(self):
        return self.role == 'customer'

    def is_provider(self):
        return self.role == 'provider'

    def is_site_admin(self):
        return self.role == 'admin' or self.is_superuser

    def __str__(self):
        name = self.get_full_name() or self.username
        return f"{name} ({self.get_role_display()})"


# ==============================================================================
# 2. Service Category Model
# Organizes various services (e.g. Electrician, Plumber, Cleaning, etc.)
# ==============================================================================
class ServiceCategory(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='🔧', help_text="Emoji or icon indicator, e.g. ⚡, 🪚")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Service Categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.icon} {self.name}"

    def active_services_count(self):
        return self.services.filter(status='active').count()


# ==============================================================================
# 3. Service Provider Profile
# Holds business details, verification status, and location coverage.
# Linked 1-to-1 with a User who has role='provider'.
# ==============================================================================
class ServiceProvider(models.Model):
    VERIFICATION_CHOICES = (
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
    )

    AVAILABILITY_CHOICES = (
        ('available', 'Available'),
        ('busy', 'Busy / Unavailable'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    business_name = models.CharField(max_length=150, help_text="Commercial or trade name")
    experience = models.PositiveIntegerField(default=0, help_text="Total years of work experience")
    address = models.TextField(help_text="Office / Workshop / Residential address")
    area = models.CharField(max_length=100, help_text="Primary service hub/area e.g. Junnar, Kothrud")
    description = models.TextField(blank=True, help_text="Brief background, certifications or specialty")
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='pending')
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business_name} - {self.area}"


# ==============================================================================
# 4. Service Model
# Specific service offering created by a verified service provider.
# ==============================================================================
class Service(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='services')
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    service_name = models.CharField(max_length=150)
    description = models.TextField()
    price_info = models.CharField(max_length=100, help_text='Estimated pricing (e.g., "Rs 300 onwards")')
    service_area = models.CharField(max_length=150, help_text='Specific areas served (e.g., "Hadapsar, Magarpatta")')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.service_name} ({self.provider.business_name})"

    def average_rating(self):
        """Calculates average rating for approved reviews only."""
        approved_reviews = self.reviews.filter(moderation_status='approved')
        if approved_reviews.exists():
            total = sum(r.rating for r in approved_reviews)
            return round(total / approved_reviews.count(), 1)
        return None

    def approved_reviews_count(self):
        return self.reviews.filter(moderation_status='approved').count()


# ==============================================================================
# 5. Service Request Model
# Booking placed by a customer for a particular service.
# ==============================================================================
class ServiceRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_requests')
    request_date = models.DateTimeField(auto_now_add=True)
    preferred_date = models.DateField(help_text="Customer's requested date of service")
    description = models.TextField(help_text="Detailed problem description or instructions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        ordering = ['-request_date']

    def __str__(self):
        return f"Request #{self.id}: {self.service.service_name} by {self.customer.username}"


# ==============================================================================
# 6. Review Model
# Feedback submitted by customers for services with moderation control.
# ==============================================================================
class Review(models.Model):
    MODERATION_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 (poor) to 5 (excellent)"
    )
    review_text = models.TextField(help_text="Customer feedback and experience")
    review_date = models.DateTimeField(auto_now_add=True)
    moderation_status = models.CharField(max_length=20, choices=MODERATION_CHOICES, default='pending')

    class Meta:
        ordering = ['-review_date']

    def __str__(self):
        return f"Review ({self.rating}★) for {self.service.service_name} by {self.customer.username}"


# ==============================================================================
# 7. Contact Enquiry Model
# Direct inquiry or question sent to a service provider.
# ==============================================================================
class ContactEnquiry(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('replied', 'Replied'),
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enquiries',
        help_text="Registered customer if logged in, else null for guest"
    )
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='enquiries')
    message = models.TextField(help_text="Message or inquiry details")
    enquiry_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    class Meta:
        verbose_name_plural = 'Contact Enquiries'
        ordering = ['-enquiry_date']

    def __str__(self):
        sender = self.customer.username if self.customer else "Guest"
        return f"Enquiry #{self.id} for {self.provider.business_name} from {sender}"
