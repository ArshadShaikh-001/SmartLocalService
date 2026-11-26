"""
Views for Smart Local Service Connect
Includes Public Pages, RBAC Authentication, and Role-Specific Dashboards.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.contrib.auth.decorators import login_required

from .models import (
    ServiceCategory,
    ServiceProvider,
    Service,
    ServiceRequest,
    Review,
    ContactEnquiry
)
from .forms import RegisterForm, LoginForm
from .decorators import role_required

User = get_user_model()


# ==============================================================================
# PUBLIC PAGES
# ==============================================================================

def home_view(request):
    """
    Landing Home Page:
    - Hero section with search form (keyword, location, category dropdown)
    - Active categories grid
    - How it works (Search -> Compare -> Contact)
    - Featured trusted services
    - Call to action
    """
    categories = ServiceCategory.objects.filter(status='active').annotate(
        service_count=Count('services', filter=Q(services__status='active'))
    )
    featured_services = Service.objects.filter(
        status='active',
        provider__verification_status='verified'
    ).select_related('provider', 'category')[:6]

    total_services = Service.objects.filter(status='active').count()
    total_providers = ServiceProvider.objects.filter(verification_status='verified').count()
    total_categories = categories.count()

    context = {
        'categories': categories,
        'featured_services': featured_services,
        'stats': {
            'services': total_services,
            'providers': total_providers,
            'categories': total_categories,
        }
    }
    return render(request, 'home.html', context)


def services_view(request):
    """
    Service Listing and Search results page.
    Receives GET parameters:
      - 'q': Search keyword (name, description, category)
      - 'location': Desired area/locality
      - 'category': Category ID or name filter
    """
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    category_id = request.GET.get('category', '').strip()

    services_queryset = Service.objects.filter(status='active').select_related('provider', 'category')

    if query:
        services_queryset = services_queryset.filter(
            Q(service_name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(provider__business_name__icontains=query)
        )

    if location:
        services_queryset = services_queryset.filter(
            Q(service_area__icontains=location) |
            Q(provider__area__icontains=location) |
            Q(provider__address__icontains=location)
        )

    if category_id:
        if category_id.isdigit():
            services_queryset = services_queryset.filter(category_id=int(category_id))
        else:
            services_queryset = services_queryset.filter(category__name__iexact=category_id)

    categories = ServiceCategory.objects.filter(status='active')

    context = {
        'services': services_queryset,
        'categories': categories,
        'query': query,
        'location': location,
        'selected_category': category_id,
        'results_count': services_queryset.count(),
    }
    return render(request, 'services.html', context)


def about_view(request):
    """About Page showcasing platform vision and BCA mini project technical details."""
    return render(request, 'about.html')


def contact_view(request):
    """Contact page with platform support details and enquiry message box."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()

        if name and email and message_text:
            messages.success(request, "Thank you! Your inquiry has been received. Our support team will reach out shortly.")
            return redirect('contact')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'contact.html')


# ==============================================================================
# AUTHENTICATION VIEWS
# ==============================================================================

def register_view(request):
    """
    User Registration View:
    - Creates Customer or Service Provider account.
    - Strictly disallows registering with 'admin' role.
    - If provider is chosen, automatically creates a linked ServiceProvider profile.
    - Hashes passwords using Django's default secure algorithm.
    """
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            full_name = cleaned['full_name'].strip()
            username = cleaned['username'].strip()
            email = cleaned['email'].strip()
            phone = cleaned['phone'].strip()
            role = cleaned['role']
            password = cleaned['password']

            # Split full name into first and last name
            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            # Create User instance
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=role
            )

            # Auto-create ServiceProvider profile if provider role
            if role == 'provider':
                ServiceProvider.objects.create(
                    user=user,
                    business_name=f"{full_name} Services",
                    experience=1,
                    address="Please update your address",
                    area="Pune",
                    description=f"Professional services offered by {full_name}.",
                    verification_status='pending',
                    availability_status='available'
                )

            # Auto log in the new user
            login(request, user)
            messages.success(
                request,
                f"Account created successfully! Welcome, {user.first_name or user.username}."
            )
            return redirect('dashboard_redirect')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """
    User Login View:
    - Allows login with either username or email address.
    - Validates credentials and active status.
    - Redirects user according to their role (customer / provider / admin).
    """
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_id = form.cleaned_data['login_id'].strip()
            password = form.cleaned_data['password']

            # Check if login_id is an email
            user_by_email = User.objects.filter(email__iexact=login_id).first()
            username = user_by_email.username if user_by_email else login_id

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(
                        request,
                        f"Logged in successfully. Welcome back, {user.get_full_name() or user.username}!"
                    )
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('dashboard_redirect')
                else:
                    messages.error(request, "Your account is inactive. Please contact support.")
            else:
                messages.error(request, "Invalid username/email or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """
    Logs out the authenticated user and redirects to the home page.
    Supports both GET and POST requests cleanly.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


# ==============================================================================
# DASHBOARDS & ROLE-BASED ROUTING
# ==============================================================================

@login_required
def dashboard_redirect_view(request):
    """
    Dispatches logged-in user to their specific dashboard based on role.
    """
    user = request.user
    if user.is_superuser or user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'provider':
        return redirect('provider_dashboard')
    else:
        return redirect('customer_dashboard')


@role_required(allowed_roles=['customer'])
def customer_dashboard_view(request):
    """
    Customer Dashboard:
    - Overview of customer's bookings and requests
    - Customer's submitted reviews
    - Quick actions to search services
    """
    requests = ServiceRequest.objects.filter(customer=request.user).select_related('service', 'service__provider')
    reviews = Review.objects.filter(customer=request.user).select_related('service')

    context = {
        'requests': requests,
        'reviews': reviews,
        'total_requests': requests.count(),
        'pending_requests': requests.filter(status='pending').count(),
    }
    return render(request, 'dashboard/customer_dashboard.html', context)


@role_required(allowed_roles=['provider'])
def provider_dashboard_view(request):
    """
    Service Provider Dashboard:
    - Provider business profile status (verified/pending, availability)
    - Services listed by this provider
    - Service requests and client enquiries
    """
    # Safe fallback if profile is missing
    profile, _ = ServiceProvider.objects.get_or_create(
        user=request.user,
        defaults={
            'business_name': f"{request.user.get_full_name() or request.user.username} Services",
            'experience': 0,
            'address': "Not specified",
            'area': "Pune",
            'description': "Service provider profile.",
        }
    )

    provider_services = Service.objects.filter(provider=profile)
    incoming_requests = ServiceRequest.objects.filter(service__provider=profile).select_related('customer', 'service')
    enquiries = ContactEnquiry.objects.filter(provider=profile).select_related('customer')

    context = {
        'profile': profile,
        'services': provider_services,
        'incoming_requests': incoming_requests,
        'enquiries': enquiries,
        'stats': {
            'total_services': provider_services.count(),
            'total_requests': incoming_requests.count(),
            'pending_requests': incoming_requests.filter(status='pending').count(),
            'total_enquiries': enquiries.count(),
        }
    }
    return render(request, 'dashboard/provider_dashboard.html', context)


@role_required(allowed_roles=['admin'])
def admin_dashboard_view(request):
    """
    Admin Dashboard:
    - Platform KPIs (total users, providers, categories, services, reviews)
    - Providers awaiting verification
    - Reviews awaiting moderation
    - Shortcut to Django Admin portal
    """
    total_users = User.objects.count()
    total_customers = User.objects.filter(role='customer').count()
    total_providers = ServiceProvider.objects.count()
    total_services = Service.objects.count()
    pending_verifications = ServiceProvider.objects.filter(verification_status='pending').count()
    pending_reviews = Review.objects.filter(moderation_status='pending').count()

    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_requests = ServiceRequest.objects.select_related('customer', 'service').order_by('-request_date')[:5]

    context = {
        'metrics': {
            'total_users': total_users,
            'total_customers': total_customers,
            'total_providers': total_providers,
            'total_services': total_services,
            'pending_verifications': pending_verifications,
            'pending_reviews': pending_reviews,
        },
        'recent_users': recent_users,
        'recent_requests': recent_requests,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)
