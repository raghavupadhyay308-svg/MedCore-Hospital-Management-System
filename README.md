# MedCore — Hospital Management System

A fully-featured desktop hospital management application built with **Python**, **PySide6 (Qt6)**, and **SQLite**. Three role-based dashboards — Admin, Doctor, and Patient — cover the entire clinical workflow from patient registration and appointment booking through consultation notes, prescriptions, and billing.

---

## Screenshots

| Login Screen | Admin Overview (with live charts) |
|---|---|
| ![Login](screenshots/01_login.png) | ![Admin Overview](screenshots/02_admin_overview.png) |

| Doctor Directory | Patient Appointments |
|---|---|
| ![Doctors](screenshots/03_admin_doctors.png) | ![Patient Portal](screenshots/04_patient_appointments.png) |

| Medical History & Prescriptions | Doctor's Daily Schedule |
|---|---|
| ![History](screenshots/05_patient_history.png) | ![Doctor Schedule](screenshots/06_doctor_schedule.png) |

---

## Tech Stack

| Layer | Technology |
|---|---|
| GUI framework | PySide6 (Qt 6 for Python) |
| Charts | PySide6 QtCharts (bar + pie) |
| Database | SQLite 3 via Python `sqlite3` |
| Password security | PBKDF2-HMAC-SHA256, per-user salt, 100,000 iterations |
| Language | Python 3.9+ |

---

## Features by Role

### 👤 Patient Portal
- Self-registration with generated Patient ID (e.g. `RAG001`)
- Secure login with hashed passwords — no plaintext stored anywhere
- Book appointments for **self or family members**, with real-time slot availability (max 3 patients per doctor-hour)
- View, reschedule, or cancel upcoming appointments
- Full medical history with diagnosis, symptoms, notes, and prescriptions per visit
- Billing history with payment status

### 🩺 Doctor Console
- Login with assigned Doctor ID (`DOC001`–`DOC005` for demo)
- Today's schedule with live stats: total / pending / completed
- One-click consultation completion — enter symptoms, diagnosis, clinical notes, and a multi-medicine prescription
- Optional automatic consultation bill generation on completion
- Patient lookup by name, ID, contact or email — full medical history on double-click
- Full appointment history with status filter

### 🏥 Admin Console
- KPI overview: total patients, active doctors, today's appointments, monthly revenue, pending bills
- Live **bar chart** (appointments last 7 days) and **pie chart** (breakdown by specialization)
- Add, edit, and activate/deactivate doctors
- Patient directory with real-time search
- Complete appointment oversight with doctor and status filters
- Manual bill creation with line items, running total, and payment method selection
- Mark bills as paid (Cash / Card / UPI)

---

## Database Schema

Nine normalized SQLite tables with foreign key enforcement:

```
admins           — admin credentials
doctors          — doctor profiles, working hours, consultation fee
patients         — patient profiles, emergency contacts
family_members   — linked dependents per patient
appointments     — bookings (patient, doctor, date, hour, status)
medical_records  — consultation outcomes (symptoms, diagnosis, notes)
prescriptions    — medicines linked to each medical record
bills            — invoice headers per patient/appointment
bill_items       — line items per bill
```

Indexes on `(doctor_id, appt_date, appt_hour)` for fast slot-availability queries.

---

## Project Structure

```
MedCore-HMS/
├── main.py                  # Entry point — MainWindow, login → dashboard routing
├── db.py                    # Database class — all SQL, schema, seeding, analytics
├── styles.py                # Global QSS stylesheet + colour palette
├── validators.py            # Input validators, date helpers
├── requirements.txt
├── ui/
│   ├── __init__.py
│   ├── widgets.py           # StatCard, NavButton, AppShell, table helpers
│   ├── login.py             # LoginWindow — patient / doctor / admin tabs + registration
│   ├── dialogs.py           # BookAppointmentDialog, CompleteAppointmentDialog, BillDialogs, etc.
│   ├── patient_portal.py    # PatientPortal — 6-page dashboard
│   ├── doctor_dashboard.py  # DoctorDashboard — 4-page dashboard
│   └── admin_dashboard.py   # AdminDashboard — 5-page dashboard with charts
└── screenshots/
```

---

## Setup & Run

```bash
# 1. Clone / unzip the project
cd MedCore-HMS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

The SQLite database (`medcore.db`) is created automatically on first run and seeded with five demo doctor accounts.

---

## Default Credentials

| Role | ID / Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Doctor | `DOC001` – `DOC005` | `doctor123` |
| Patient | Register on the login screen | (set during registration) |

---

## Key Engineering Decisions

- **Zero plaintext passwords** — all credentials are hashed with PBKDF2-HMAC-SHA256 and a 128-bit random salt per user.
- **Slot enforcement** — the booking layer rejects any slot that already has 3 appointments for that doctor-hour, returning a clear `ValueError` that the UI surfaces to the user.
- **Separation of concerns** — `db.py` owns all SQL; dialogs and dashboards never write raw queries.
- **Modular UI shell** — `AppShell` (sidebar + topbar + content area) is instantiated once per role; individual page widgets are swapped in on demand to keep memory usage low.
- **Offline-first** — entirely local SQLite, no network dependency, deployable on any hospital workstation.

---

## Resume Talking Points

- Built a **multi-role Python desktop application** (3,000+ lines) with PySide6 and SQLite, replacing a C console app with a polished GUI featuring login, CRUD workflows, and analytics dashboards.
- Implemented **PBKDF2-HMAC-SHA256 password hashing** with per-user salts — no plaintext credentials stored anywhere in the system.
- Designed a **normalized 9-table SQLite schema** with foreign key constraints and performance indexes, supporting concurrent slot enforcement (max 3 bookings/doctor-hour).
- Integrated **QtCharts** for real-time bar and pie chart analytics on the admin overview — zero external charting libraries required.
- Architected a reusable `AppShell` component (sidebar + topbar + page routing) that all three role dashboards inherit, reducing boilerplate by ~40%.

---

*Developed by Raghav Upadhyay · B.Tech AI/ML, GEHU Dehradun · [github.com/raghavupadhyay308](https://github.com/raghavupadhyay308)*
