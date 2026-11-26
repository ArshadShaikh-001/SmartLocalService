"""
Forms for Smart Local Service Connect
Handles user registration, login, and validation.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class RegisterForm(forms.Form):
    """
    Registration form allowing users to sign up either as a Customer
    or a Service Provider. Admin role is strictly disallowed from registration.
    """
    ROLE_CHOICES = (
        ('customer', 'Customer (Looking for services)'),
        ('provider', 'Service Provider (Offering local services)'),
    )

    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Ramesh Patil',
            'class': 'form-input',
            'autocomplete': 'name'
        }),
        label="Full Name"
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a unique username',
            'class': 'form-input',
            'autocomplete': 'username'
        }),
        label="Username"
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'e.g. ramesh@example.com',
            'class': 'form-input',
            'autocomplete': 'email'
        }),
        label="Email Address"
    )

    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. 9822012345',
            'class': 'form-input',
            'autocomplete': 'tel'
        }),
        label="Phone Number"
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-input form-select'}),
        label="Register As"
    )

    password = forms.CharField(
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'At least 6 characters',
            'class': 'form-input',
            'autocomplete': 'new-password'
        }),
        label="Password"
    )

    confirm_password = forms.CharField(
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Re-enter your password',
            'class': 'form-input',
            'autocomplete': 'new-password'
        }),
        label="Confirm Password"
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        # Clean basic phone number check
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            raise ValidationError("Please provide a valid phone number with at least 10 digits.")
        return phone

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role not in ['customer', 'provider']:
            raise ValidationError("Invalid role selected. Only Customer or Provider registrations are allowed.")
        return role

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please re-enter carefully.")

        return cleaned_data


class LoginForm(forms.Form):
    """
    Login form accepting either username or email address + password.
    """
    login_id = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username or Email',
            'class': 'form-input',
            'autocomplete': 'username'
        }),
        label="Username or Email"
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-input',
            'autocomplete': 'current-password'
        }),
        label="Password"
    )


class ServiceRequestForm(forms.Form):
    """
    Form for customers to book / request a specific service.
    Validates that preferred_date is not in the past and description has at least 10 characters.
    """
    preferred_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input',
        }),
        label="Preferred Date of Service"
    )

    description = forms.CharField(
        required=True,
        min_length=10,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Describe your issue or what work needs to be done (minimum 10 characters)...',
            'class': 'form-input',
        }),
        label="Service Requirements & Notes"
    )

    def clean_preferred_date(self):
        from datetime import date
        pref_date = self.cleaned_data.get('preferred_date')
        if pref_date and pref_date < date.today():
            raise ValidationError("The preferred service date cannot be in the past. Please select today or a future date.")
        return pref_date

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if len(desc) < 10:
            raise ValidationError("Please provide at least 10 characters describing the required work.")
        return desc


class ContactEnquiryForm(forms.Form):
    """
    Form for customers to send a direct message / enquiry to a service provider.
    Requires at least 10 characters.
    """
    message = forms.CharField(
        required=True,
        min_length=10,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Write your message or ask a question (minimum 10 characters)...',
            'class': 'form-input',
        }),
        label="Inquiry Message"
    )

    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()
        if len(msg) < 10:
            raise ValidationError("Please write at least 10 characters in your inquiry message.")
        return msg


class ReviewForm(forms.Form):
    """
    Form for customers to rate and review a completed service.
    """
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        required=True,
        widget=forms.HiddenInput(attrs={'id': 'id_rating', 'value': '5'}),
        label="Rating (1 to 5 Stars)"
    )

    review_text = forms.CharField(
        required=True,
        min_length=10,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Share your honest feedback about this service (minimum 10 characters)...',
            'class': 'form-input',
        }),
        label="Review Comments"
    )

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None or rating < 1 or rating > 5:
            raise ValidationError("Rating must be between 1 and 5 stars.")
        return rating

    def clean_review_text(self):
        text = self.cleaned_data.get('review_text', '').strip()
        if len(text) < 10:
            raise ValidationError("Please write at least 10 characters of feedback.")
        return text


class CustomerProfileForm(forms.ModelForm):
    """
    Form for customers to edit their basic profile information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email address is already used by another account.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            raise ValidationError("Please provide a valid phone number with at least 10 digits.")
        return phone
