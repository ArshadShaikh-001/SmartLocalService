"""
Management Command to Seed Initial Demo Data for Smart Local Service Connect
BCA Mini Project Demonstration Data.
Usage: python manage.py seed_data
"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import (
    User,
    ServiceCategory,
    ServiceProvider,
    Service,
    ServiceRequest,
    Review,
    ContactEnquiry
)


class Command(BaseCommand):
    help = "Seeds database with demo Admin, Customers, Service Providers, Categories, Services, and Reviews"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demo data for Smart Local Service Connect..."))

        with transaction.atomic():
            # ------------------------------------------------------------------
            # 1. Clear Existing Data (Idempotent seed)
            # ------------------------------------------------------------------
            Review.objects.all().delete()
            ServiceRequest.objects.all().delete()
            ContactEnquiry.objects.all().delete()
            Service.objects.all().delete()
            ServiceProvider.objects.all().delete()
            ServiceCategory.objects.all().delete()
            User.objects.all().delete()

            # ------------------------------------------------------------------
            # 2. Create Admin Account
            # ------------------------------------------------------------------
            admin_user = User.objects.create_superuser(
                username="admin",
                email="admin@smartlocal.com",
                password="admin123",
                first_name="System",
                last_name="Administrator",
                phone="9876543210",
                role="admin"
            )
            self.stdout.write(self.style.SUCCESS("✓ Admin user created: admin / admin123"))

            # ------------------------------------------------------------------
            # 3. Create 3 Customers
            # ------------------------------------------------------------------
            customer_data = [
                {
                    "username": "rahul_patil",
                    "first_name": "Rahul",
                    "last_name": "Patil",
                    "email": "rahul@example.com",
                    "phone": "9822011111",
                },
                {
                    "username": "priya_sharma",
                    "first_name": "Priya",
                    "last_name": "Sharma",
                    "email": "priya@example.com",
                    "phone": "9822022222",
                },
                {
                    "username": "amit_deshmukh",
                    "first_name": "Amit",
                    "last_name": "Deshmukh",
                    "email": "amit@example.com",
                    "phone": "9822033333",
                },
            ]

            customers = []
            for c in customer_data:
                user = User.objects.create_user(
                    username=c["username"],
                    email=c["email"],
                    password="demo1234",
                    first_name=c["first_name"],
                    last_name=c["last_name"],
                    phone=c["phone"],
                    role="customer"
                )
                customers.append(user)
            self.stdout.write(self.style.SUCCESS(f"✓ {len(customers)} Customer accounts created."))

            # ------------------------------------------------------------------
            # 4. Create 8 Service Categories
            # ------------------------------------------------------------------
            category_data = [
                {
                    "name": "Electrician",
                    "icon": "⚡",
                    "description": "Wiring, switchboard repair, appliance installation, and emergency power issues.",
                },
                {
                    "name": "Plumber",
                    "icon": "🔧",
                    "description": "Water leakage fix, pipe fitting, sanitary installations, and tap replacements.",
                },
                {
                    "name": "Carpenter",
                    "icon": "🪚",
                    "description": "Furniture repairs, door lock fitting, modular fittings, and custom woodcraft.",
                },
                {
                    "name": "Cleaning",
                    "icon": "🧹",
                    "description": "Full home deep cleaning, kitchen/bathroom sanitization, and sofa washing.",
                },
                {
                    "name": "Appliance Repair",
                    "icon": "🔌",
                    "description": "AC, refrigerator, washing machine, microwave, and geyser maintenance.",
                },
                {
                    "name": "Tutor",
                    "icon": "📚",
                    "description": "Home tutors and online guidance for School, BCA, MCA, and Engineering subjects.",
                },
                {
                    "name": "Vehicle Mechanic",
                    "icon": "🚗",
                    "description": "On-demand two-wheeler & four-wheeler doorstep servicing and breakdown aid.",
                },
                {
                    "name": "Painter",
                    "icon": "🎨",
                    "description": "Interior and exterior wall painting, waterproof coating, and texture designs.",
                },
            ]

            category_map = {}
            for cat in category_data:
                obj = ServiceCategory.objects.create(
                    name=cat["name"],
                    icon=cat["icon"],
                    description=cat["description"],
                    status="active"
                )
                category_map[cat["name"]] = obj
            self.stdout.write(self.style.SUCCESS(f"✓ {len(category_map)} Service Categories created."))

            # ------------------------------------------------------------------
            # 5. Create 6 Verified Service Providers (Pune region areas)
            # ------------------------------------------------------------------
            provider_configs = [
                {
                    "username": "ramesh_services",
                    "first_name": "Ramesh",
                    "last_name": "Shinde",
                    "email": "ramesh@example.com",
                    "phone": "9850012345",
                    "business_name": "Shinde Electricals & Home Services",
                    "experience": 7,
                    "address": "Near Bus Stand, Vadgaon Sahani, Pune 410502",
                    "area": "Vadgaon Sahani",
                    "description": "Licensed residential and commercial electrician with 7+ years of trusted track record.",
                },
                {
                    "username": "ganesh_plumbing",
                    "first_name": "Ganesh",
                    "last_name": "Tambe",
                    "email": "ganesh@example.com",
                    "phone": "9850023456",
                    "business_name": "Tambe Plumbing Works",
                    "experience": 5,
                    "address": "Main Market Road, Narayangaon, Pune 410504",
                    "area": "Narayangaon",
                    "description": "Expert plumber offering pipe leakage troubleshooting, motor installation, and sanitary fittings.",
                },
                {
                    "username": "sachin_carpentry",
                    "first_name": "Sachin",
                    "last_name": "Jadhav",
                    "email": "sachin@example.com",
                    "phone": "9850034567",
                    "business_name": "Modern Woodcraft & Furniture",
                    "experience": 9,
                    "address": "Shivaji Chowk, Junnar, Pune 410502",
                    "area": "Junnar",
                    "description": "Skilled carpenter specializing in modern cabinetry, door lock mechanisms, and custom woodworking.",
                },
                {
                    "username": "sunita_cleaning",
                    "first_name": "Sunita",
                    "last_name": "Gaikwad",
                    "email": "sunita@example.com",
                    "phone": "9850045678",
                    "business_name": "SparkleClean Deep Cleaning Services",
                    "experience": 4,
                    "address": "DP Road, Kothrud, Pune 411038",
                    "area": "Kothrud",
                    "description": "Eco-friendly deep cleaning specialists for apartments, villas, and modern office spaces.",
                },
                {
                    "username": "vikram_appliances",
                    "first_name": "Vikram",
                    "last_name": "Kadam",
                    "email": "vikram@example.com",
                    "phone": "9850056789",
                    "business_name": "QuickFix Appliance Care",
                    "experience": 6,
                    "address": "Solapur Road, Hadapsar, Pune 411028",
                    "area": "Hadapsar",
                    "description": "Certified technician for inverter AC, multi-door refrigerators, and fully automatic washing machines.",
                },
                {
                    "username": "nilesh_mechanic",
                    "first_name": "Nilesh",
                    "last_name": "Wagh",
                    "email": "nilesh@example.com",
                    "phone": "9850067890",
                    "business_name": "Pune AutoCare & Mobile Garage",
                    "experience": 8,
                    "address": "Near Gadital, Hadapsar, Pune 411028",
                    "area": "Hadapsar",
                    "description": "Mobile mechanic offering 24/7 breakdown assistance, oil changes, and comprehensive tune-ups.",
                },
            ]

            provider_map = {}
            for p in provider_configs:
                user = User.objects.create_user(
                    username=p["username"],
                    email=p["email"],
                    password="demo1234",
                    first_name=p["first_name"],
                    last_name=p["last_name"],
                    phone=p["phone"],
                    role="provider"
                )
                provider = ServiceProvider.objects.create(
                    user=user,
                    business_name=p["business_name"],
                    experience=p["experience"],
                    address=p["address"],
                    area=p["area"],
                    description=p["description"],
                    verification_status="verified",
                    availability_status="available"
                )
                provider_map[p["username"]] = provider
            self.stdout.write(self.style.SUCCESS(f"✓ {len(provider_map)} Verified Service Providers created."))

            # ------------------------------------------------------------------
            # 6. Create 12 Services spread across categories
            # ------------------------------------------------------------------
            service_configs = [
                # Electrician (Ramesh Shinde)
                {
                    "provider": "ramesh_services",
                    "category": "Electrician",
                    "service_name": "Fan, Light & Switchboard Repair",
                    "description": "Safe diagnosis and fixing of faulty switches, MCBs, ceiling fans, and indoor lighting fixtures.",
                    "price_info": "Rs 250 onwards",
                    "service_area": "Vadgaon Sahani, Junnar, Narayangaon",
                },
                {
                    "provider": "ramesh_services",
                    "category": "Electrician",
                    "service_name": "Complete Home Wiring & Inverter Setup",
                    "description": "Full house concealed or casing wiring, safety earthing checks, and battery inverter installation.",
                    "price_info": "Rs 1,500 onwards",
                    "service_area": "Vadgaon Sahani and surrounding villages",
                },
                # Plumber (Ganesh Tambe)
                {
                    "provider": "ganesh_plumbing",
                    "category": "Plumber",
                    "service_name": "Pipe Leakage & Tap Fitting",
                    "description": "Immediate stoppage of overhead and underground pipe leaks, replacement of taps and diverters.",
                    "price_info": "Rs 300 onwards",
                    "service_area": "Narayangaon, Junnar, Alephata",
                },
                {
                    "provider": "ganesh_plumbing",
                    "category": "Plumber",
                    "service_name": "Bathroom Sanitary & Geyser Connection",
                    "description": "Complete western commode, washbasin, shower panel, and water heater plumbing line setup.",
                    "price_info": "Rs 800 onwards",
                    "service_area": "Narayangaon & neighboring sectors",
                },
                # Carpenter (Sachin Jadhav)
                {
                    "provider": "sachin_carpentry",
                    "category": "Carpenter",
                    "service_name": "Custom Furniture & Wardrobe Repair",
                    "description": "Fixing sliding wardrobes, hinges, channel rollers, plywood alignment, and general polish.",
                    "price_info": "Rs 600 onwards",
                    "service_area": "Junnar, Narayangaon, Otur",
                },
                {
                    "provider": "sachin_carpentry",
                    "category": "Carpenter",
                    "service_name": "Main Door Lock & Hardware Installation",
                    "description": "Precision fitting for digital locks, deadbolts, safety chains, peep holes, and door handles.",
                    "price_info": "Rs 350 onwards",
                    "service_area": "Junnar and nearby towns",
                },
                # Cleaning (Sunita Gaikwad)
                {
                    "provider": "sunita_cleaning",
                    "category": "Cleaning",
                    "service_name": "Full Home Deep Cleaning (1BHK/2BHK/3BHK)",
                    "description": "Comprehensive mechanized cleaning including balcony, windows, floor buffing, and high-dust areas.",
                    "price_info": "Rs 1,499 onwards",
                    "service_area": "Kothrud, Karve Nagar, Deccan, Pune",
                },
                {
                    "provider": "sunita_cleaning",
                    "category": "Cleaning",
                    "service_name": "Kitchen Degreasing & Chimney Cleaning",
                    "description": "Removal of stubborn grease, oil stains, exhaust cleaning, tile disinfection, and cabinet wipe-down.",
                    "price_info": "Rs 599 onwards",
                    "service_area": "Kothrud, Bavdhan, Warje",
                },
                # Appliance Repair (Vikram Kadam)
                {
                    "provider": "vikram_appliances",
                    "category": "Appliance Repair",
                    "service_name": "Washing Machine & Microwave Servicing",
                    "description": "Fixing drum vibration, drainage errors, PCB board faults, and heating component issues.",
                    "price_info": "Rs 400 onwards",
                    "service_area": "Hadapsar, Magarpatta, Amanora",
                },
                {
                    "provider": "vikram_appliances",
                    "category": "Appliance Repair",
                    "service_name": "Refrigerator Gas Charging & Cooling Repair",
                    "description": "Single/Double door fridge compressor diagnosis, thermostat setting, and leak-free gas refill.",
                    "price_info": "Rs 750 onwards",
                    "service_area": "Hadapsar, Kharadi, Fursungi",
                },
                # Vehicle Mechanic (Nilesh Wagh)
                {
                    "provider": "nilesh_mechanic",
                    "category": "Vehicle Mechanic",
                    "service_name": "Bike & Scooter Doorstep Servicing",
                    "description": "Engine oil change, carburetor tuning, brake adjustment, chain lubrication, and electrical check.",
                    "price_info": "Rs 350 onwards",
                    "service_area": "Hadapsar, Fatima Nagar, Wanowrie",
                },
                {
                    "provider": "nilesh_mechanic",
                    "category": "Vehicle Mechanic",
                    "service_name": "Car Periodic Maintenance & Inspection",
                    "description": "40-point health inspection, coolant top-up, battery health check, brake bleed, and engine scan.",
                    "price_info": "Rs 1,200 onwards",
                    "service_area": "Hadapsar, Kondhwa, Camp Pune",
                },
            ]

            services = []
            for sc in service_configs:
                srv = Service.objects.create(
                    provider=provider_map[sc["provider"]],
                    category=category_map[sc["category"]],
                    service_name=sc["service_name"],
                    description=sc["description"],
                    price_info=sc["price_info"],
                    service_area=sc["service_area"],
                    status="active"
                )
                services.append(srv)
            self.stdout.write(self.style.SUCCESS(f"✓ {len(services)} Services created across categories."))

            # ------------------------------------------------------------------
            # 7. Create Approved Reviews
            # ------------------------------------------------------------------
            reviews_data = [
                {
                    "customer": customers[0],  # Rahul
                    "service": services[0],   # Fan, Light & Switchboard Repair
                    "rating": 5,
                    "review_text": "Prompt response and solved the short circuit issue within 30 minutes! Very respectful and fair charges.",
                    "moderation_status": "approved",
                },
                {
                    "customer": customers[1],  # Priya
                    "service": services[2],   # Pipe Leakage & Tap Fitting
                    "rating": 4,
                    "review_text": "Very polite and fixed the leaking bathroom pipe quickly in Narayangaon. Reasonable charges.",
                    "moderation_status": "approved",
                },
                {
                    "customer": customers[2],  # Amit
                    "service": services[6],   # Full Home Deep Cleaning
                    "rating": 5,
                    "review_text": "Our apartment in Kothrud looks spotless! Sunita's team arrived right on time with professional machines.",
                    "moderation_status": "approved",
                },
                {
                    "customer": customers[0],  # Rahul
                    "service": services[9],   # Refrigerator Repair
                    "rating": 5,
                    "review_text": "Fixed our refrigerator cooling problem on the same day. Transparent explanation of the compressor issue.",
                    "moderation_status": "approved",
                },
                {
                    "customer": customers[1],  # Priya
                    "service": services[4],   # Custom Furniture & Wardrobe Repair
                    "rating": 5,
                    "review_text": "Sachin restored our antique wooden cabinet beautifully. Great craftsmanship right here in Junnar.",
                    "moderation_status": "approved",
                },
            ]

            for r in reviews_data:
                Review.objects.create(
                    customer=r["customer"],
                    service=r["service"],
                    rating=r["rating"],
                    review_text=r["review_text"],
                    moderation_status=r["moderation_status"]
                )
            self.stdout.write(self.style.SUCCESS(f"✓ {len(reviews_data)} Approved Reviews created."))

            # ------------------------------------------------------------------
            # 8. Create a sample Service Request and Contact Enquiry for realism
            # ------------------------------------------------------------------
            ServiceRequest.objects.create(
                customer=customers[0],
                service=services[0],
                preferred_date=date.today() + timedelta(days=2),
                description="Need 2 ceiling fans installed in newly renovated bedrooms.",
                status="pending"
            )

            ContactEnquiry.objects.create(
                customer=customers[1],
                provider=provider_map["ramesh_services"],
                message="Do you provide emergency electric repair service on Sundays in Vadgaon?",
                status="new"
            )

        # ----------------------------------------------------------------------
        # Print Summary of Demo Logins
        # ----------------------------------------------------------------------
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("SMART LOCAL SERVICE CONNECT - DEMO LOGIN CREDENTIALS"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"{'Role':<18} | {'Username':<20} | {'Password':<12} | {'Notes / Area'}")
        self.stdout.write("-" * 70)
        self.stdout.write(f"{'Administrator':<18} | {'admin':<20} | {'admin123':<12} | System Admin Access")
        self.stdout.write("-" * 70)
        self.stdout.write(f"{'Customer 1':<18} | {'rahul_patil':<20} | {'demo1234':<12} | Rahul Patil (User)")
        self.stdout.write(f"{'Customer 2':<18} | {'priya_sharma':<20} | {'demo1234':<12} | Priya Sharma (User)")
        self.stdout.write(f"{'Customer 3':<18} | {'amit_deshmukh':<20} | {'demo1234':<12} | Amit Deshmukh (User)")
        self.stdout.write("-" * 70)
        self.stdout.write(f"{'Provider 1':<18} | {'ramesh_services':<20} | {'demo1234':<12} | Electrician (Vadgaon Sahani)")
        self.stdout.write(f"{'Provider 2':<18} | {'ganesh_plumbing':<20} | {'demo1234':<12} | Plumber (Narayangaon)")
        self.stdout.write(f"{'Provider 3':<18} | {'sachin_carpentry':<20} | {'demo1234':<12} | Carpenter (Junnar)")
        self.stdout.write(f"{'Provider 4':<18} | {'sunita_cleaning':<20} | {'demo1234':<12} | Cleaning (Kothrud)")
        self.stdout.write(f"{'Provider 5':<18} | {'vikram_appliances':<20} | {'demo1234':<12} | Appliances (Hadapsar)")
        self.stdout.write(f"{'Provider 6':<18} | {'nilesh_mechanic':<20} | {'demo1234':<12} | Mechanic (Hadapsar)")
        self.stdout.write("=" * 70 + "\n")
