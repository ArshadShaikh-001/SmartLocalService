"""
Role-based Access Control (RBAC) Decorators for Smart Local Service Connect
Used to restrict view access based on user role (customer, provider, admin).
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def role_required(allowed_roles=None):
    """
    Decorator to restrict access to users belonging to specific roles.
    Example:
        @role_required(allowed_roles=['customer'])
        def customer_dashboard(request):
            ...
    """
    if allowed_roles is None:
        allowed_roles = []

    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check 1: User must be authenticated
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                login_url = reverse('login')
                return redirect(f"{login_url}?next={request.path}")

            # Check 2: User must possess one of the allowed roles
            user_role = getattr(request.user, 'role', 'customer')
            
            # Superuser / admin can view admin sections or override if needed
            is_permitted = (user_role in allowed_roles) or (request.user.is_superuser and 'admin' in allowed_roles)

            if not is_permitted:
                messages.error(request, f"Access denied. You do not have permission as a '{request.user.get_role_display()}'.")
                return redirect('dashboard_redirect')

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
