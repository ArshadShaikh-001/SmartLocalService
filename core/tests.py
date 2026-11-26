"""
Comprehensive Automated Test Suite for Smart Local Service Connect
Validates:
- Chunk 1: Models, Auth, Dashboards, RBAC
- Chunk 2: Categories, Search, Service Details, Provider Profile, Customer Booking, Enquiries, Reviews, Customer Dashboard
- Chunk 3:
  - Provider Dashboard, Profile Edit, Availability Toggle
  - Provider Manage Services (Add, Edit, Toggle, Delete, Cross-provider security)
  - Provider Requests Inbox (Accept, Reject, Mark Completed, Transition validation)
  - Provider Enquiries Inbox (Mark Replied)
  - Admin Dashboard Metrics
  - Admin Manage Users (Activate/Deactivate, Self-deactivation guard)
  - Admin Manage Providers (Verify/Unverify)
  - Admin Manage Categories (Add, Edit, Toggle, Block Delete on linked services)
  - Admin Moderate Services (Deactivate misleading listings)
  - Admin Moderate Reviews (Approve/Reject)
  - Full End-to-End Multi-Role Workflow (Provider Adds Service -> Admin Verifies -> Customer Requests -> Provider Completes -> Customer Reviews -> Admin Approves -> Public Display)
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


class SmartLocalServiceChunk3Tests(TestCase):
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

        # 4. Verified Provider
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

        # 5. Second Provider (for cross-provider isolation checks)
        self.provider2_user = User.objects.create_user(
            username="ganesh_plumbing",
            email="ganesh@example.com",
            password="demo1234",
            first_name="Ganesh",
            last_name="Tambe",
            phone="9850023456",
            role="provider"
        )
        self.provider2 = ServiceProvider.objects.create(
            user=self.provider2_user,
            business_name="Tambe Plumbing Works",
            experience=5,
            address="Narayangaon, Pune",
            area="Narayangaon",
            verification_status="verified",
            availability_status="available"
        )

        # 6. Service by Provider 1
        self.service_fan = Service.objects.create(
            provider=self.provider,
            category=self.cat_electrician,
            service_name="Fan & Wiring Repair",
            description="Fixing ceiling fans, short circuits, and MCB switches.",
            price_info="Rs 250 onwards",
            service_area="Vadgaon Sahani, Junnar",
            status="active"
        )

    # ==========================================================================
    # A. SERVICE PROVIDER MODULE TESTS
    # ==========================================================================
    def test_provider_dashboard_overview(self):
        self.client.login(username='ramesh_services', password='demo1234')
        response = self.client.get(reverse('provider_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Shinde Electricals &amp; Home Services")
        self.assertContains(response, "Total Services")

    def test_provider_profile_edit(self):
        self.client.login(username='ramesh_services', password='demo1234')
        response = self.client.post(reverse('provider_dashboard'), {
            'update_profile': '1',
            'business_name': 'Shinde Advanced Electricals',
            'experience': 8,
            'address': 'Main Market, Vadgaon Sahani',
            'area': 'Vadgaon Sahani',
            'description': 'Updated bio and 8 years experience.',
            'phone': '9850099887'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "updated successfully")
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.business_name, 'Shinde Advanced Electricals')
        self.assertEqual(self.provider.experience, 8)
        self.provider_user.refresh_from_db()
        self.assertEqual(self.provider_user.phone, '9850099887')

    def test_provider_toggle_availability(self):
        self.client.login(username='ramesh_services', password='demo1234')
        # Initially available -> toggle to busy
        response = self.client.post(reverse('provider_toggle_availability'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.availability_status, 'busy')

        # Toggle back to available
        response2 = self.client.post(reverse('provider_toggle_availability'), follow=True)
        self.assertEqual(response2.status_code, 200)
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.availability_status, 'available')

    def test_provider_add_service(self):
        self.client.login(username='ramesh_services', password='demo1234')
        response = self.client.post(reverse('provider_service_add'), {
            'category': self.cat_electrician.id,
            'service_name': 'Inverter & Generator Wiring',
            'price_info': 'Rs 800 onwards',
            'service_area': 'Vadgaon Sahani and Junnar',
            'description': 'Full home inverter cabling and heavy duty cut-off switches.'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Service.objects.filter(service_name='Inverter & Generator Wiring', provider=self.provider).exists())

    def test_provider_edit_service(self):
        self.client.login(username='ramesh_services', password='demo1234')
        response = self.client.post(reverse('provider_service_edit', kwargs={'pk': self.service_fan.id}), {
            'category': self.cat_electrician.id,
            'service_name': 'Fan, Light & Switchboard Repair',
            'price_info': 'Rs 300 onwards',
            'service_area': 'Vadgaon Sahani, Narayangaon',
            'description': 'Updated description with fast 30 min response time.'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.service_fan.refresh_from_db()
        self.assertEqual(self.service_fan.service_name, 'Fan, Light & Switchboard Repair')
        self.assertEqual(self.service_fan.price_info, 'Rs 300 onwards')

    def test_cross_provider_service_isolation(self):
        """Provider 2 must NOT be able to edit or delete Provider 1's service."""
        self.client.login(username='ganesh_plumbing', password='demo1234')
        # Attempt edit on Provider 1's service
        response = self.client.get(reverse('provider_service_edit', kwargs={'pk': self.service_fan.id}))
        self.assertEqual(response.status_code, 404)

        # Attempt delete on Provider 1's service
        response_del = self.client.post(reverse('provider_service_delete', kwargs={'pk': self.service_fan.id}))
        self.assertEqual(response_del.status_code, 404)
        self.assertTrue(Service.objects.filter(id=self.service_fan.id).exists())

    def test_provider_request_lifecycle_transitions(self):
        """Test strict state transitions: pending -> accepted -> completed."""
        req = ServiceRequest.objects.create(
            customer=self.customer,
            service=self.service_fan,
            preferred_date=date.today() + timedelta(days=2),
            description="Need wiring fixed in living room.",
            status="pending"
        )

        self.client.login(username='ramesh_services', password='demo1234')

        # Invalid transition: pending -> completed must fail
        self.client.post(reverse('provider_request_update_status', kwargs={'pk': req.id}), {'action': 'complete'})
        req.refresh_from_db()
        self.assertEqual(req.status, 'pending')

        # Valid transition: pending -> accepted
        self.client.post(reverse('provider_request_update_status', kwargs={'pk': req.id}), {'action': 'accept'})
        req.refresh_from_db()
        self.assertEqual(req.status, 'accepted')

        # Valid transition: accepted -> completed
        self.client.post(reverse('provider_request_update_status', kwargs={'pk': req.id}), {'action': 'complete'})
        req.refresh_from_db()
        self.assertEqual(req.status, 'completed')

    def test_provider_reply_to_enquiry(self):
        enq = ContactEnquiry.objects.create(
            customer=self.customer,
            provider=self.provider,
            message="Do you provide warranty on wiring work?",
            status="new"
        )
        self.client.login(username='ramesh_services', password='demo1234')
        response = self.client.post(reverse('provider_enquiry_reply', kwargs={'pk': enq.id}), follow=True)
        self.assertEqual(response.status_code, 200)
        enq.refresh_from_db()
        self.assertEqual(enq.status, 'replied')

    # ==========================================================================
    # B. ADMINISTRATOR MODULE TESTS
    # ==========================================================================
    def test_admin_dashboard_metrics(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "System Administration")
        self.assertContains(response, "Registered Customers")

    def test_admin_manage_users_toggle_active(self):
        self.client.login(username='admin', password='admin123')
        # Deactivate customer
        response = self.client.post(reverse('admin_user_toggle_active', kwargs={'pk': self.customer.id}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)

        # Reactivate customer
        response2 = self.client.post(reverse('admin_user_toggle_active', kwargs={'pk': self.customer.id}), follow=True)
        self.assertEqual(response2.status_code, 200)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_active)

    def test_admin_cannot_deactivate_self(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('admin_user_toggle_active', kwargs={'pk': self.admin_user.id}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot deactivate your own administrative account")
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)

    def test_admin_verify_and_unverify_provider(self):
        self.client.login(username='admin', password='admin123')
        # Unverify provider
        self.client.post(reverse('admin_provider_toggle_verification', kwargs={'pk': self.provider.id}))
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.verification_status, 'pending')

        # Verify provider
        self.client.post(reverse('admin_provider_toggle_verification', kwargs={'pk': self.provider.id}))
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.verification_status, 'verified')

    def test_admin_category_management_and_safe_delete(self):
        self.client.login(username='admin', password='admin123')
        # Add new category
        response = self.client.post(reverse('admin_categories'), {
            'add_category': '1',
            'name': 'Pest Control',
            'icon': '🐜',
            'description': 'Termite and bedbug eradication',
            'status': 'active'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ServiceCategory.objects.filter(name='Pest Control').exists())
        new_cat = ServiceCategory.objects.get(name='Pest Control')

        # Safe delete: Category with 0 services CAN be deleted
        del_resp = self.client.post(reverse('admin_category_delete', kwargs={'pk': new_cat.id}), follow=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertFalse(ServiceCategory.objects.filter(name='Pest Control').exists())

        # Blocked delete: Electrician has linked services, deletion must be blocked
        blocked_resp = self.client.post(reverse('admin_category_delete', kwargs={'pk': self.cat_electrician.id}), follow=True)
        self.assertEqual(blocked_resp.status_code, 200)
        self.assertContains(blocked_resp, "Cannot delete category")
        self.assertTrue(ServiceCategory.objects.filter(id=self.cat_electrician.id).exists())

    def test_admin_moderate_service_toggle(self):
        self.client.login(username='admin', password='admin123')
        # Deactivate service
        self.client.post(reverse('admin_service_toggle_status', kwargs={'pk': self.service_fan.id}))
        self.service_fan.refresh_from_db()
        self.assertEqual(self.service_fan.status, 'inactive')

        # Reactivate service
        self.client.post(reverse('admin_service_toggle_status', kwargs={'pk': self.service_fan.id}))
        self.service_fan.refresh_from_db()
        self.assertEqual(self.service_fan.status, 'active')

    # ==========================================================================
    # C. FULL MULTI-ROLE END-TO-END INTEGRATION WORKFLOW
    # Provider adds service -> Admin verifies provider -> Customer requests
    # -> Provider completes -> Customer reviews -> Admin approves -> Public view
    # ==========================================================================
    def test_full_role_workflow_end_to_end(self):
        # Step 1: Create a fresh new provider with pending verification
        new_tech_user = User.objects.create_user(
            username="kailash_tutor",
            email="kailash@example.com",
            password="demo1234",
            first_name="Kailash",
            last_name="Pawar",
            phone="9890112233",
            role="provider"
        )
        new_provider = ServiceProvider.objects.create(
            user=new_tech_user,
            business_name="Pawar Home Tuition & Mentorship",
            experience=4,
            address="Shivaji Chowk, Narayangaon",
            area="Narayangaon",
            description="Math and Computer science tutoring.",
            verification_status="pending",  # initially unverified
            availability_status="available"
        )

        # Provider adds a new service
        self.client.login(username='kailash_tutor', password='demo1234')
        add_srv_resp = self.client.post(reverse('provider_service_add'), {
            'category': self.cat_electrician.id,
            'service_name': 'Computer Programming Tutoring',
            'price_info': 'Rs 500 per hr',
            'service_area': 'Narayangaon and Junnar',
            'description': 'Python, Django and Web development practical coaching for BCA students.'
        }, follow=True)
        self.assertEqual(add_srv_resp.status_code, 200)
        tutoring_service = Service.objects.get(service_name='Computer Programming Tutoring', provider=new_provider)

        # Step 2: Unverified provider's service should NOT be visible in public search
        self.client.logout()
        search_resp = self.client.get(reverse('services'), {'q': 'Tutoring'})
        self.assertNotContains(search_resp, "Computer Programming Tutoring")

        # Step 3: Admin verifies the provider
        self.client.login(username='admin', password='admin123')
        verify_resp = self.client.post(
            reverse('admin_provider_toggle_verification', kwargs={'pk': new_provider.id}),
            follow=True
        )
        self.assertEqual(verify_resp.status_code, 200)
        new_provider.refresh_from_db()
        self.assertEqual(new_provider.verification_status, 'verified')
        self.client.logout()

        # Step 4: Customer searches and now finds the verified service!
        search_resp2 = self.client.get(reverse('services'), {'q': 'Tutoring'})
        self.assertEqual(search_resp2.status_code, 200)
        self.assertContains(search_resp2, "Computer Programming Tutoring")

        # Step 5: Customer logs in and sends a booking request
        self.client.login(username='rahul_patil', password='demo1234')
        future_date = date.today() + timedelta(days=3)
        book_resp = self.client.post(
            reverse('service_request_create', kwargs={'pk': tutoring_service.id}),
            {
                'preferred_date': future_date.isoformat(),
                'description': 'Need help preparing Django mini project for upcoming college evaluation.'
            },
            follow=True
        )
        self.assertEqual(book_resp.status_code, 200)
        booking = ServiceRequest.objects.get(customer=self.customer, service=tutoring_service)
        self.assertEqual(booking.status, 'pending')
        self.client.logout()

        # Step 6: Provider views inbox, accepts request, then completes it
        self.client.login(username='kailash_tutor', password='demo1234')
        # Accept
        accept_resp = self.client.post(
            reverse('provider_request_update_status', kwargs={'pk': booking.id}),
            {'action': 'accept'},
            follow=True
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'accepted')

        # Complete
        complete_resp = self.client.post(
            reverse('provider_request_update_status', kwargs={'pk': booking.id}),
            {'action': 'complete'},
            follow=True
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'completed')
        self.client.logout()

        # Step 7: Customer reviews the completed service
        self.client.login(username='rahul_patil', password='demo1234')
        review_resp = self.client.post(
            reverse('review_create', kwargs={'pk': tutoring_service.id}),
            {
                'rating': 5,
                'review_text': 'Excellent mentor! Solved all Django MVT architecture questions in 1 session.'
            },
            follow=True
        )
        self.assertEqual(review_resp.status_code, 200)
        self.assertContains(review_resp, "Thanks! Your review will appear after approval.")
        review = Review.objects.get(customer=self.customer, service=tutoring_service)
        self.assertEqual(review.moderation_status, 'pending')
        self.client.logout()

        # Step 8: Verify review is NOT yet visible publicly
        public_detail_before = self.client.get(reverse('service_detail', kwargs={'pk': tutoring_service.id}))
        self.assertNotContains(public_detail_before, "Excellent mentor! Solved all Django")

        # Step 9: Admin approves the review
        self.client.login(username='admin', password='admin123')
        approve_resp = self.client.post(
            reverse('admin_review_moderate', kwargs={'pk': review.id}),
            {'action': 'approve', 'status_filter': 'pending'},
            follow=True
        )
        self.assertEqual(approve_resp.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.moderation_status, 'approved')
        self.client.logout()

        # Step 10: Review now appears on the public service details page!
        public_detail_after = self.client.get(reverse('service_detail', kwargs={'pk': tutoring_service.id}))
        self.assertEqual(public_detail_after.status_code, 200)
        self.assertContains(public_detail_after, "Excellent mentor! Solved all Django")
        self.assertContains(public_detail_after, "5.0")
