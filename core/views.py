"""
Views for Smart Local Service Connect
Includes Public Pages, RBAC Authentication, Customer Flow, and Role-Specific Dashboards.
"""

from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.db.models import Q, Avg, Count, F
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse

from .models import (
    ServiceCategory,
    ServiceProvider,
    Service,
    ServiceRequest,
    Review,
    ContactEnquiry
)
from .forms import (
    RegisterForm,
    LoginForm,
    ServiceRequestForm,
    ContactEnquiryForm,
    ReviewForm,
    CustomerProfileForm
)
from .decorators import role_required

User = get_user_model()


# ==============================================================================
# PUBLIC PAGES & CATALOG
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
        service_count=Count(
            'services',
            filter=Q(services__status='active', services__provider__verification_status='verified')
        )
    )
    featured_services = Service.objects.filter(
        status='active',
        provider__verification_status='verified'
    ).select_related('provider', 'category').annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__moderation_status='approved')),
        review_count=Count('reviews', filter=Q(reviews__moderation_status='approved'))
    )[:6]

    total_services = Service.objects.filter(status='active', provider__verification_status='verified').count()
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


def categories_view(request):
    """
    Service Categories Catalog Page:
    Grid of all active categories with icon, name, description,
    and number of active services in each.
    """
    categories = ServiceCategory.objects.filter(status='active').annotate(
        active_services_count=Count(
            'services',
            filter=Q(services__status='active', services__provider__verification_status='verified')
        )
    )
    return render(request, 'categories.html', {'categories': categories})


def services_view(request):
    """
    Service Listing and Search results page.
    Filters:
      - 'q': Keyword matching service name, description, provider business name
      - 'category': Category ID or name
      - 'location': Matches service_area, provider area, or address
      - 'sort': 'rating', 'experience', 'newest'
      - 'page': Pagination (9 items per page)
    Security: Only shows active services whose provider is verified.
    """
    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    category_id = request.GET.get('category', '').strip()
    sort = request.GET.get('sort', 'newest').strip()

    # Base query: Active services with verified providers, using select_related and annotate to prevent N+1 queries
    services_queryset = Service.objects.filter(
        status='active',
        provider__verification_status='verified'
    ).select_related(
        'provider', 'provider__user', 'category'
    ).annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__moderation_status='approved')),
        review_count=Count('reviews', filter=Q(reviews__moderation_status='approved'))
    )

    # 1. Keyword search
    if query:
        services_queryset = services_queryset.filter(
            Q(service_name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(provider__business_name__icontains=query)
        )

    # 2. Location search
    if location:
        services_queryset = services_queryset.filter(
            Q(service_area__icontains=location) |
            Q(provider__area__icontains=location) |
            Q(provider__address__icontains=location)
        )

    # 3. Category filter
    if category_id:
        if category_id.isdigit():
            services_queryset = services_queryset.filter(category_id=int(category_id))
        else:
            services_queryset = services_queryset.filter(category__name__iexact=category_id)

    # 4. Sorting
    if sort == 'rating':
        services_queryset = services_queryset.order_by(F('avg_rating').desc(nulls_last=True), '-created_at')
    elif sort == 'experience':
        services_queryset = services_queryset.order_by('-provider__experience', '-created_at')
    else:  # newest
        services_queryset = services_queryset.order_by('-created_at')

    # Total matching records before pagination
    total_matching = services_queryset.count()

    # 5. Pagination: 9 per page
    paginator = Paginator(services_queryset, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = ServiceCategory.objects.filter(status='active')

    context = {
        'page_obj': page_obj,
        'services': page_obj.object_list,
        'categories': categories,
        'query': query,
        'location': location,
        'selected_category': category_id,
        'selected_sort': sort,
        'results_count': total_matching,
    }
    return render(request, 'services.html', context)


def service_detail_view(request, pk):
    """
    Service Details Page:
    - Service details (description, price, area, category)
    - Summary card of provider with link to provider profile
    - Approved reviews only, with average rating
    - Action forms: Send Enquiry, Request This Service, and Post Review
    - Role restrictions applied: only role=customer can request, enquire, or review.
    """
    service = get_object_or_404(
        Service.objects.select_related('provider', 'provider__user', 'category').annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__moderation_status='approved')),
            review_count=Count('reviews', filter=Q(reviews__moderation_status='approved'))
        ),
        pk=pk,
        status='active'
    )

    # Approved reviews for this service
    reviews = service.reviews.filter(moderation_status='approved').select_related('customer').order_by('-review_date')

    # Check review eligibility for logged-in customers
    can_review = False
    has_completed_booking = False
    existing_user_review = None

    if request.user.is_authenticated and request.user.is_customer():
        # Check if customer has any completed request for this service
        has_completed_booking = ServiceRequest.objects.filter(
            customer=request.user,
            service=service,
            status='completed'
        ).exists()

        # Check if user already submitted a review (pending or approved)
        existing_user_review = Review.objects.filter(
            customer=request.user,
            service=service
        ).first()

        can_review = has_completed_booking and (existing_user_review is None)

    context = {
        'service': service,
        'provider': service.provider,
        'reviews': reviews,
        'can_review': can_review,
        'has_completed_booking': has_completed_booking,
        'existing_user_review': existing_user_review,
        'request_form': ServiceRequestForm(),
        'enquiry_form': ContactEnquiryForm(),
        'review_form': ReviewForm(),
        'today': date.today().isoformat(),
    }
    return render(request, 'service_detail.html', context)


def provider_profile_view(request, pk):
    """
    Provider Profile Page:
    - Business name, experience, address, area, description, availability, verified badge
    - All active services by this provider
    - All approved reviews across their services
    - Contact enquiry form
    """
    provider = get_object_or_404(
        ServiceProvider.objects.select_related('user'),
        pk=pk
    )

    # Provider's active services
    provider_services = provider.services.filter(status='active').select_related('category').annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__moderation_status='approved')),
        review_count=Count('reviews', filter=Q(reviews__moderation_status='approved'))
    )

    # All approved reviews across all services offered by this provider
    approved_reviews = Review.objects.filter(
        service__provider=provider,
        moderation_status='approved'
    ).select_related('customer', 'service').order_by('-review_date')

    context = {
        'provider': provider,
        'services': provider_services,
        'reviews': approved_reviews,
        'enquiry_form': ContactEnquiryForm(),
    }
    return render(request, 'provider_profile.html', context)


# ==============================================================================
# CUSTOMER ACTIONS (BOOKINGS, ENQUIRIES, REVIEWS)
# ==============================================================================

def service_request_create_view(request, pk):
    """
    Handles submission of a booking request for a service.
    Requires customer authentication.
    """
    service = get_object_or_404(Service, pk=pk, status='active')

    if not request.user.is_authenticated:
        messages.warning(request, "Please log in as a customer to book this service.")
        login_url = reverse('login')
        next_path = reverse('service_detail', kwargs={'pk': pk})
        return redirect(f"{login_url}?next={next_path}")

    if not request.user.is_customer():
        messages.error(request, "Only customer accounts can book services. You are currently logged in with a non-customer role.")
        return redirect('service_detail', pk=pk)

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            ServiceRequest.objects.create(
                customer=request.user,
                service=service,
                preferred_date=form.cleaned_data['preferred_date'],
                description=form.cleaned_data['description'],
                status='pending'
            )
            messages.success(
                request,
                f"Booking request for '{service.service_name}' submitted successfully! You can track its status in your dashboard."
            )
            return redirect('customer_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

    return redirect('service_detail', pk=pk)


def service_enquiry_create_view(request, pk):
    """
    Handles sending a direct enquiry to a provider regarding a service.
    Requires customer authentication.
    """
    service = get_object_or_404(Service.objects.select_related('provider'), pk=pk)

    if not request.user.is_authenticated:
        messages.warning(request, "Please log in as a customer to send an inquiry.")
        login_url = reverse('login')
        next_path = reverse('service_detail', kwargs={'pk': pk})
        return redirect(f"{login_url}?next={next_path}")

    if not request.user.is_customer():
        messages.error(request, "Only customer accounts can send service inquiries.")
        return redirect('service_detail', pk=pk)

    if request.method == 'POST':
        form = ContactEnquiryForm(request.POST)
        if form.is_valid():
            ContactEnquiry.objects.create(
                customer=request.user,
                provider=service.provider,
                message=form.cleaned_data['message'],
                status='new'
            )
            messages.success(request, f"Your inquiry has been sent to {service.provider.business_name}.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

    return redirect('service_detail', pk=pk)


def provider_enquiry_create_view(request, pk):
    """
    Handles sending an enquiry directly from a provider's profile page.
    """
    provider = get_object_or_404(ServiceProvider, pk=pk)

    if not request.user.is_authenticated:
        messages.warning(request, "Please log in as a customer to send an inquiry.")
        login_url = reverse('login')
        next_path = reverse('provider_profile', kwargs={'pk': pk})
        return redirect(f"{login_url}?next={next_path}")

    if not request.user.is_customer():
        messages.error(request, "Only customer accounts can send provider inquiries.")
        return redirect('provider_profile', pk=pk)

    if request.method == 'POST':
        form = ContactEnquiryForm(request.POST)
        if form.is_valid():
            ContactEnquiry.objects.create(
                customer=request.user,
                provider=provider,
                message=form.cleaned_data['message'],
                status='new'
            )
            messages.success(request, f"Your inquiry has been sent to {provider.business_name}.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

    return redirect('provider_profile', pk=pk)


def review_create_view(request, pk):
    """
    Submits a rating (1-5) and review for a service.
    Enforces rules:
      - Must be customer role
      - Must have a 'completed' service request for this service
      - One review per customer per service
      - Saved with moderation_status='pending'
    """
    service = get_object_or_404(Service, pk=pk, status='active')

    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to submit a review.")
        login_url = reverse('login')
        next_path = reverse('service_detail', kwargs={'pk': pk})
        return redirect(f"{login_url}?next={next_path}")

    if not request.user.is_customer():
        messages.error(request, "Only customers can submit reviews.")
        return redirect('service_detail', pk=pk)

    # Eligibility check: Must have completed booking
    has_completed = ServiceRequest.objects.filter(
        customer=request.user,
        service=service,
        status='completed'
    ).exists()

    if not has_completed:
        messages.error(request, "You can only review services for which you have a completed booking.")
        return redirect('service_detail', pk=pk)

    # Duplicate check: One review per customer per service
    if Review.objects.filter(customer=request.user, service=service).exists():
        messages.warning(request, "You have already submitted a review for this service.")
        return redirect('service_detail', pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                customer=request.user,
                service=service,
                rating=form.cleaned_data['rating'],
                review_text=form.cleaned_data['review_text'],
                moderation_status='pending'
            )
            messages.success(request, "Thanks! Your review will appear after approval.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

    return redirect('service_detail', pk=pk)


def cancel_request_view(request, pk):
    """
    Allows a customer to cancel their own service request while it is still 'pending'.
    """
    if not request.user.is_authenticated or not request.user.is_customer():
        messages.error(request, "Unauthorized action.")
        return redirect('home')

    service_request = get_object_or_404(ServiceRequest, pk=pk, customer=request.user)

    if request.method == 'POST':
        if service_request.status == 'pending':
            service_request.status = 'cancelled'
            service_request.save()
            messages.success(request, f"Service request #{service_request.id} has been cancelled successfully.")
        else:
            messages.warning(request, f"Request #{service_request.id} cannot be cancelled because it is already '{service_request.get_status_display()}'.")

    return redirect('customer_dashboard')


# ==============================================================================
# STATIC & INFO PAGES
# ==============================================================================

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

            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=role
            )

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
    - Redirects user according to their role.
    """
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login_id = form.cleaned_data['login_id'].strip()
            password = form.cleaned_data['password']

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
    - Profile info with an edit form (name, phone, email)
    - "My Service Requests" table with status badge and cancel action for pending requests
    - "My Enquiries" table with status
    - "My Reviews" table with moderation status
    """
    user = request.user

    # Handle Profile Update Form
    if request.method == 'POST' and 'update_profile' in request.POST:
        profile_form = CustomerProfileForm(request.POST, instance=user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile information has been updated successfully!")
            return redirect('customer_dashboard')
        else:
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        profile_form = CustomerProfileForm(instance=user)

    requests = ServiceRequest.objects.filter(customer=user).select_related('service', 'service__provider')
    enquiries = ContactEnquiry.objects.filter(customer=user).select_related('provider')
    reviews = Review.objects.filter(customer=user).select_related('service')

    context = {
        'profile_form': profile_form,
        'requests': requests,
        'enquiries': enquiries,
        'reviews': reviews,
        'total_requests': requests.count(),
        'pending_requests': requests.filter(status='pending').count(),
    }
    return render(request, 'dashboard/customer_dashboard.html', context)


@role_required(allowed_roles=['provider'])
def provider_dashboard_view(request):
    """
    Service Provider Dashboard:
    - Provider business profile status
    - Services listed by this provider
    - Service requests and client enquiries
    """
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
    - Platform KPIs
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
