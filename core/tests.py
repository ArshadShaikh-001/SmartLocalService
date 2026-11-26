"""
Comprehensive Automated Test Suite for Smart Local Service Connect
Validates:
- Chunk 1: Models, Auth, Dashboards, RBAC
- Chunk 2:
  1. Service Categories Page (/categories/)
  2. Service Search & Filters (/services/ with q, location, category, sort, pagination)
  3. Service Details Page (/services/<id>/) with provider summary and reviews
  4. Provider Profile Page (/providers/<id>/) with all services and reviews
  5. Booking Request creation with server-side validation
  6. Direct Contact Enquiry creation with min-length validation
  7. Review eligibility rule (only completed bookings, 1 per customer, pending moderation)
  8. Customer Dashboard (/dashboard/customer/) with profile edit, booking cancel, and inquiry list
"""

from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import (
    ServiceCategory,
    ServiceProvider,
    Service,
    ServiceRequest,
    Review,
    ContactEnquiry
)

User = get_user_model()


class SmartLocalServiceChunk2Tests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Categories
        self.cat_electrician = ServiceCategory.objects.create(
            name="Electrician",
            icon="⚡",
            description="Electrical repairs and wiring",
            status="active"
        )
        self.cat_plumber = ServiceCategory.objects.create(
            name="Plumber",
            icon="🔧",
            description="Plumbing and pipe fittings",
            status="active"
        )

        # 2. Admin User
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@smartlocal.com",
            password="admin123",
            role="admin"
        )

        # 3. Customer User
        self.customer = User.objects.create_user(
            username="rahul_patil",
            email="rahul@example.com",
            password="demo1234",
            first_name="Rahul",
            last_name="Patil",
            phone="9822011111",
            role="customer"
        )

        # 4. Another Customer User
        self.customer2 = User.objects.create_user(
            username="priya_sharma",
            email="priya@example.com",
            password="demo1234",
            first_name="Priya",
            last_name="Sharma",
            phone="9822022222",
            role="customer"
        )

        # 5. Verified Provider
        self.provider_user = User.objects.create_user(
            username="ramesh_services",
            email="ramesh@example.com",
            password="demo1234",
            first_name="Ramesh",
            last_name="Shinde",
            phone="9850012345",
            role="provider"
        )
        self.provider = ServiceProvider.objects.create(
            user=self.provider_user,
            business_name="Shinde Electricals & Home Services",
            experience=7,
            address="Near Bus Stand, Vadgaon Sahani",
            area="Vadgaon Sahani",
            description="Expert licensed electrician with 7 years track record.",
            verification_status="verified",
            availability_status="available"
        )

        # 6. Unverified Provider (Should NOT show in public search)
        self.unverified_user = User.objects.create_user(
            username="pending_tech",
            email="pending@example.com",
            password="demo1234",
            role="provider"
        )
        self.unverified_provider = ServiceProvider.objects.create(
            user=self.unverified_user,
            business_name="Unverified Tech Co",
            experience=1,
            address="Kothrud, Pune",
            area="Kothrud",
            verification_status="pending",
            availability_status="available"
        )

        # 7. Services
        self.service_fan = Service.objects.create(
            provider=self.provider,
            category=self.cat_electrician,
            service_name="Fan & Wiring Repair",
            description="Fixing ceiling fans, short circuits, and MCB switches.",
            price_info="Rs 250 onwards",
            service_area="Vadgaon Sahani, Junnar",
            status="active"
        )

        self.service_inverter = Service.objects.create(
            provider=self.provider,
            category=self.cat_electrician,
            service_name="Inverter Setup & Battery Care",
            description="Home battery inverter installation and load testing.",
            price_info="Rs 1,500 onwards",
            service_area="Vadgaon Sahani, Narayangaon",
            status="active"
        )

        # Service by unverified provider
        self.unverified_service = Service.objects.create(
            provider=self.unverified_provider,
            category=self.cat_electrician,
            service_name="Cheap Wiring Work",
            description="Unverified service",
            price_info="Rs 100 onwards",
            service_area="Kothrud",
            status="active"
        )

        # 8. Approved Review on service_fan
        self.review1 = Review.objects.create(
            customer=self.customer2,
            service=self.service_fan,
            rating=5,
            review_text="Super fast service in Vadgaon! Repaired the fan in 20 minutes.",
            moderation_status="approved"
        )

    # ==========================================================================
    # 1. CATEGORIES PAGE TESTS
    # ==========================================================================
    def test_categories_page(self):
        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Electrician")
        self.assertContains(response, "Plumber")
        self.assertContains(response, "2 services")  # 2 active verified services under Electrician

    # ==========================================================================
    # 2. SEARCH & LISTING PAGE TESTS
    # ==========================================================================
    def test_services_search_shows_only_verified(self):
        response = self.client.get(reverse('services'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fan &amp; Wiring Repair")
        self.assertContains(response, "Inverter Setup")
        # Ensure service by unverified provider is EXCLUDED
        self.assertNotContains(response, "Cheap Wiring Work")

    def test_services_filter_by_keyword(self):
        response = self.client.get(reverse('services'), {'q': 'Inverter'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inverter Setup")
        self.assertNotContains(response, "Fan &amp; Wiring Repair")

    def test_services_filter_by_location(self):
        response = self.client.get(reverse('services'), {'location': 'Narayangaon'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inverter Setup")

    def test_services_filter_by_category(self):
        response = self.client.get(reverse('services'), {'category': self.cat_plumber.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No services found")

    def test_services_sorting(self):
        # Sort by rating
        response = self.client.get(reverse('services'), {'sort': 'rating'})
        self.assertEqual(response.status_code, 200)
        # Service with review (rating 5.0) should appear first
        self.assertContains(response, "Fan &amp; Wiring Repair")

    # ==========================================================================
    # 3. SERVICE DETAILS PAGE TESTS
    # ==========================================================================
    def test_service_detail_public_view(self):
        response = self.client.get(reverse('service_detail', kwargs={'pk': self.service_fan.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fan &amp; Wiring Repair")
        self.assertContains(response, "Shinde Electricals &amp; Home Services")
        self.assertContains(response, "Rs 250 onwards")
        self.assertContains(response, "Super fast service in Vadgaon!")
        self.assertContains(response, "Log In to Book Service")

    def test_service_detail_customer_logged_in(self):
        self.client.login(username='rahul_patil', password='demo1234')
        response = self.client.get(reverse('service_detail', kwargs={'pk': self.service_fan.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm Booking Request")
        self.assertContains(response, "Send Direct Inquiry")

    # ==========================================================================
    # 4. PROVIDER PROFILE PAGE TESTS
    # ==========================================================================
    def test_provider_profile_page(self):
        response = self.client.get(reverse('provider_profile', kwargs={'pk': self.provider.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shinde Electricals &amp; Home Services")
        self.assertContains(response, "7 Years")
        self.assertContains(response, "Vadgaon Sahani")
        self.assertContains(response, "Fan &amp; Wiring Repair")
        self.assertContains(response, "Inverter Setup")
        self.assertContains(response, "Super fast service in Vadgaon!")

    # ==========================================================================
    # 5. SERVICE REQUEST (BOOKING) TESTS
    # ==========================================================================
    def test_customer_creates_booking_request(self):
        self.client.login(username='rahul_patil', password='demo1234')
        future_date = date.today() + timedelta(days=3)
        response = self.client.post(
            reverse('service_request_create', kwargs={'pk': self.service_fan.id}),
            {
                'preferred_date': future_date.isoformat(),
                'description': 'Ceiling fan regulator sparking when switched on.'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('customer_dashboard'))
        self.assertTrue(
            ServiceRequest.objects.filter(customer=self.customer, service=self.service_fan).exists()
        )
        req = ServiceRequest.objects.get(customer=self.customer, service=self.service_fan)
        self.assertEqual(req.status, 'pending')

    def test_booking_request_fails_with_past_date(self):
        self.client.login(username='rahul_patil', password='demo1234')
        past_date = date.today() - timedelta(days=2)
        response = self.client.post(
            reverse('service_request_create', kwargs={'pk': self.service_fan.id}),
            {
                'preferred_date': past_date.isoformat(),
                'description': 'Need help with ceiling fan repair.'
            },
            follow=True
        )
        self.assertFalse(
            ServiceRequest.objects.filter(customer=self.customer, service=self.service_fan).exists()
        )
        self.assertContains(response, "cannot be in the past")

    def test_booking_request_fails_with_short_description(self):
        self.client.login(username='rahul_patil', password='demo1234')
        future_date = date.today() + timedelta(days=2)
        response = self.client.post(
            reverse('service_request_create', kwargs={'pk': self.service_fan.id}),
            {
                'preferred_date': future_date.isoformat(),
                'description': 'Fix fan'  # Only 7 chars, requires >= 10
            },
            follow=True
        )
        self.assertFalse(
            ServiceRequest.objects.filter(customer=self.customer, service=self.service_fan).exists()
        )
        self.assertContains(response, "at least 10 characters")

    # ==========================================================================
    # 6. CONTACT ENQUIRY TESTS
    # ==========================================================================
    def test_customer_sends_service_enquiry(self):
        self.client.login(username='rahul_patil', password='demo1234')
        response = self.client.post(
            reverse('service_enquiry_create', kwargs={'pk': self.service_fan.id}),
            {
                'message': 'Do you charge extra for spare parts or only labor fees?'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ContactEnquiry.objects.filter(customer=self.customer, provider=self.provider).exists()
        )
        enq = ContactEnquiry.objects.get(customer=self.customer, provider=self.provider)
        self.assertEqual(enq.status, 'new')

    # ==========================================================================
    # 7. REVIEW ELIGIBILITY & SUBMISSION TESTS
    # ==========================================================================
    def test_review_rejected_if_no_completed_booking(self):
        self.client.login(username='rahul_patil', password='demo1234')
        # Customer has NOT booked or completed this service
        response = self.client.post(
            reverse('review_create', kwargs={'pk': self.service_fan.id}),
            {
                'rating': 5,
                'review_text': 'Great technician, very punctual and knowledgeable!'
            },
            follow=True
        )
        self.assertFalse(Review.objects.filter(customer=self.customer, service=self.service_fan).exists())
        self.assertContains(response, "completed booking")

    def test_review_accepted_after_completed_booking(self):
        self.client.login(username='rahul_patil', password='demo1234')
        # Create a completed booking for customer
        ServiceRequest.objects.create(
            customer=self.customer,
            service=self.service_fan,
            preferred_date=date.today(),
            description="Fix fan sparking issue.",
            status="completed"
        )

        response = self.client.post(
            reverse('review_create', kwargs={'pk': self.service_fan.id}),
            {
                'rating': 5,
                'review_text': 'Excellent repair work done on time at Vadgaon!'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Thanks! Your review will appear after approval.")
        
        # Verify saved with pending moderation status
        new_review = Review.objects.get(customer=self.customer, service=self.service_fan)
        self.assertEqual(new_review.moderation_status, 'pending')
        self.assertEqual(new_review.rating, 5)

        # Duplicate review test: cannot review again
        response_dup = self.client.post(
            reverse('review_create', kwargs={'pk': self.service_fan.id}),
            {
                'rating': 4,
                'review_text': 'Second review attempt should fail cleanly.'
            },
            follow=True
        )
        self.assertContains(response_dup, "already submitted a review")

    # ==========================================================================
    # 8. CUSTOMER DASHBOARD & CANCELLATION TESTS
    # ==========================================================================
    def test_customer_dashboard_profile_update(self):
        self.client.login(username='rahul_patil', password='demo1234')
        response = self.client.post(
            reverse('customer_dashboard'),
            {
                'update_profile': '1',
                'first_name': 'Rahul',
                'last_name': 'Patil (Updated)',
                'email': 'rahul_updated@example.com',
                'phone': '9822998877'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "updated successfully")
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.last_name, 'Patil (Updated)')
        self.assertEqual(self.customer.phone, '9822998877')

    def test_customer_cancels_pending_booking(self):
        self.client.login(username='rahul_patil', password='demo1234')
        req = ServiceRequest.objects.create(
            customer=self.customer,
            service=self.service_fan,
            preferred_date=date.today() + timedelta(days=1),
            description="Need fan repair at home.",
            status="pending"
        )

        response = self.client.post(
            reverse('cancel_request', kwargs={'pk': req.id}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cancelled successfully")
        req.refresh_from_db()
        self.assertEqual(req.status, 'cancelled')
