# Smart Local Service Connect
**A Digital Platform for Finding Trusted Local Services**  
*Bachelor of Computer Applications (BCA) Mini Project*

---

## 📌 Project Overview
Smart Local Service Connect is a clean, modern web application that bridges the gap between verified local service providers (electricians, plumbers, carpenters, cleaning technicians, appliance mechanics) and household customers in urban and semi-urban localities around Pune (such as Junnar, Narayangaon, Vadgaon Sahani, Hadapsar, and Kothrud).

---

## 🚀 Tech Stack
- **Backend:** Python Django 6.1.3 (latest stable)
- **Frontend:** HTML5, Semantic Custom CSS3 (Mobile-Responsive, Flexbox/Grid, Hamburger Menu), Vanilla JavaScript
- **Database:** SQLite (default for development/demo), modular configuration ready for MySQL switch
- **Security:** Django CSRF Protection, PBKDF2 Password Hashing, Role-Based Access Control (RBAC)

---

## 🗄️ Database Models (7 Core Entities)
1. **Custom User (`core.User`):** Extends `AbstractUser` with `phone`, `role` (`customer`, `provider`, `admin`), and active status.
2. **ServiceCategory (`core.ServiceCategory`):** Category name, description, emoji icon, status (`active`/`inactive`).
3. **ServiceProvider (`core.ServiceProvider`):** OneToOne to User, business name, experience, address, area, verification status (`pending`/`verified`), availability (`available`/`busy`).
4. **Service (`core.Service`):** ForeignKeys to Provider and Category, service name, description, price info, coverage area, status.
5. **ServiceRequest (`core.ServiceRequest`):** Customer booking requests with preferred date, description, status (`pending`, `accepted`, `rejected`, `completed`).
6. **Review (`core.Review`):** Customer feedback with 1–5 star ratings, feedback text, and moderation status (`pending`, `approved`, `rejected`).
7. **ContactEnquiry (`core.ContactEnquiry`):** Direct customer messages to service providers.

---

## 🔑 Demo Login Credentials (from `seed_data`)

| Role | Username | Password | Role / Coverage Area |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | System Admin & Moderation |
| **Customer 1** | `rahul_patil` | `demo1234` | Rahul Patil |
| **Customer 2** | `priya_sharma` | `demo1234` | Priya Sharma |
| **Customer 3** | `amit_deshmukh` | `demo1234` | Amit Deshmukh |
| **Provider 1** | `ramesh_services` | `demo1234` | Electrician (Vadgaon Sahani) |
| **Provider 2** | `ganesh_plumbing` | `demo1234` | Plumber (Narayangaon) |
| **Provider 3** | `sachin_carpentry` | `demo1234` | Carpenter (Junnar) |
| **Provider 4** | `sunita_cleaning` | `demo1234` | Cleaning Specialist (Kothrud) |
| **Provider 5** | `vikram_appliances`| `demo1234` | Appliance Care (Hadapsar) |
| **Provider 6** | `nilesh_mechanic` | `demo1234` | Mobile Mechanic (Hadapsar) |

*(Note: Users can also log in using their email address!)*

---

## ⚙️ Quick Start Commands

```bash
# 1. Navigate to the project directory
cd /home/arshad/Downloads/SmartLocalService

# 2. Apply database migrations
python3 manage.py makemigrations
python3 manage.py migrate

# 3. Seed demo data (Creates admin, 3 customers, 6 providers, 8 categories, 12 services, and reviews)
python3 manage.py seed_data

# 4. Run automated test suite
python3 manage.py test

# 5. Start the development server
python3 manage.py runserver 127.0.0.1:8000
```

Open your browser and visit: **http://127.0.0.1:8000/**

---

## 🐬 Switching from SQLite to MySQL (For College Viva / Evaluation)
In [settings.py](file:///home/arshad/Downloads/SmartLocalService/smart_local_service/settings.py):
1. Comment out the default SQLite `DATABASES` block.
2. Uncomment the MySQL `DATABASES` block.
3. Install the MySQL database connector:
   ```bash
   pip install mysqlclient
   ```
4. Create the MySQL database:
   ```sql
   CREATE DATABASE smart_local_service_db CHARACTER SET utf8mb4;
   ```
5. Run migrations:
   ```bash
   python3 manage.py migrate
   python3 manage.py seed_data
   ```
