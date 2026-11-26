"""
Automated Test Suite for Smart Local Service Connect
Validates:
- Public URL endpoints
- Role-based registration & profile auto-creation
- Dual authentication (username or email)
- Role-based redirects and access control
- Logout flow
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import ServiceCategory, ServiceProvider, Service

User = get_user_model()


class SmartLocalServiceTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Seed categories
        self.category = ServiceCategory.objects.create(
            name="Electrician",
            icon="⚡",
            description="Electrical services",
            status="active"
        )

        # Create demo admin
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@smartlocal.com",
            password="admin123",
            role="admin"
        )

        # Create demo customer
        self.customer_user = User.objects.create_user(
            username="rahul_patil",
            email="rahul@example.com",
            password="demo1234",
            phone="9822011111",
            role="customer"
        )

        # Create demo provider
        self.provider_user = User.objects.create_user(
            username="ramesh_services",
            email="ramesh@example.com",
            password="demo1234",
            phone="9850012345",
            role="provider"
        )
        self.provider_profile = ServiceProvider.objects.create(
            user=self.provider_user,
            business_name="Shinde Electricals & Home Services",
            experience=7,
            address="Near Bus Stand, Vadgaon Sahani",
            area="Vadgaon Sahani",
            verification_status="verified",
            availability_status="available"
        )

        # Create sample service
        self.service = Service.objects.create(
            provider=self.provider_profile,
            category=self.category,
            service_name="Fan & Wiring Repair",
            description="Fixing switches and fan wiring",
            price_info="Rs 250 onwards",
            service_area="Vadgaon Sahani, Junnar",
            status="active"
        )

    # --------------------------------------------------------------------------
    # Public Pages Tests
    # --------------------------------------------------------------------------
    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Smart Local Service Connect")
        self.assertContains(response, "Electrician")

    def test_about_page(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bachelor of Computer Applications")

    def test_contact_page(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Operating Hours")

    def test_services_page_and_search(self):
        # Base listing
        response = self.client.get(reverse('services'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fan &amp; Wiring Repair")

        # Search by keyword
        response_search = self.client.get(reverse('services'), {'q': 'Wiring'})
        self.assertEqual(response_search.status_code, 200)
        self.assertContains(response_search, "Fan &amp; Wiring Repair")

        # Search with non-matching query
        response_empty = self.client.get(reverse('services'), {'q': 'NonExistentService123'})
        self.assertEqual(response_empty.status_code, 200)
        self.assertContains(response_empty, "No Services Found")

    # --------------------------------------------------------------------------
    # Registration Tests
    # --------------------------------------------------------------------------
    def test_customer_registration(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Snehal Joshi',
            'username': 'snehal_joshi',
            'email': 'snehal@example.com',
            'phone': '9890012345',
            'role': 'customer',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='snehal_joshi').exists())
        new_user = User.objects.get(username='snehal_joshi')
        self.assertEqual(new_user.role, 'customer')
        self.assertFalse(ServiceProvider.objects.filter(user=new_user).exists())

    def test_provider_registration_auto_creates_profile(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Mahesh Shirole',
            'username': 'mahesh_shirole',
            'email': 'mahesh@example.com',
            'phone': '9890054321',
            'role': 'provider',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='mahesh_shirole').exists())
        new_user = User.objects.get(username='mahesh_shirole')
        self.assertEqual(new_user.role, 'provider')
        # Check that ServiceProvider profile was automatically created
        self.assertTrue(ServiceProvider.objects.filter(user=new_user).exists())
        profile = ServiceProvider.objects.get(user=new_user)
        self.assertEqual(profile.verification_status, 'pending')

    def test_registration_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Test User',
            'username': 'test_user',
            'email': 'test@example.com',
            'phone': '9890000000',
            'role': 'customer',
            'password': 'password123',
            'confirm_password': 'password999'
        }, follow=True)

        self.assertFalse(User.objects.filter(username='test_user').exists())
        self.assertContains(response, "Passwords do not match")

    # --------------------------------------------------------------------------
    # Login & Role-Based Routing Tests
    # --------------------------------------------------------------------------
    def test_login_by_username_customer(self):
        response = self.client.post(reverse('login'), {
            'login_id': 'rahul_patil',
            'password': 'demo1234'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('customer_dashboard'))
        self.assertContains(response, "Customer Portal")

    def test_login_by_email_customer(self):
        response = self.client.post(reverse('login'), {
            'login_id': 'rahul@example.com',
            'password': 'demo1234'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('customer_dashboard'))

    def test_login_provider(self):
        response = self.client.post(reverse('login'), {
            'login_id': 'ramesh_services',
            'password': 'demo1234'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('provider_dashboard'))
        self.assertContains(response, "Shinde Electricals &amp; Home Services")

    def test_login_admin(self):
        response = self.client.post(reverse('login'), {
            'login_id': 'admin',
            'password': 'admin123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertContains(response, "System Administration")

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'login_id': 'rahul_patil',
            'password': 'wrongpassword'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/email or password")

    # --------------------------------------------------------------------------
    # Role Protection & Logout Tests
    # --------------------------------------------------------------------------
    def test_role_protection_customer_accessing_admin(self):
        self.client.login(username='rahul_patil', password='demo1234')
        response = self.client.get(reverse('admin_dashboard'), follow=True)
        # Should be redirected away with error message
        self.assertRedirects(response, reverse('customer_dashboard'))
        self.assertContains(response, "Access denied")

    def test_logout(self):
        self.client.login(username='rahul_patil', password='demo1234')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('home'))
        self.assertContains(response, "logged out successfully")
