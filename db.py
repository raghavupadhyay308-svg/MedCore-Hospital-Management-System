"""
db.py
Database layer for MedCore Hospital Management System.

Uses SQLite3 with a normalized relational schema (5NF-friendly):
  admins, doctors, patients, family_members, appointments,
  medical_records, prescriptions, bills, bill_items

All access goes through the Database class below so the rest of the
application never writes raw SQL inline. Foreign keys are enforced,
and every write that can fail (slot conflicts, duplicate logins, etc.)
is validated before it touches disk.
"""

import sqlite3
import os
import hashlib
import binascii
import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medcore.db")

MAX_SLOTS_PER_HOUR = 3
MIN_NOTICE_HOURS = 2
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASS = "admin123"


# ---------------------------------------------------------------------------
# Password hashing (PBKDF2-HMAC-SHA256, per-user salt, no plaintext storage)
# ---------------------------------------------------------------------------
def hash_password(password: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return binascii.hexlify(salt).decode(), binascii.hexlify(dk).decode()


def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    try:
        salt = binascii.unhexlify(salt_hex)
    except (binascii.Error, TypeError):
        return False
    _, dk_hex = hash_password(password, salt)
    return dk_hex == hash_hex


def now_iso():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Database:
    def __init__(self, path=DB_PATH):
        self.path = path
        first_run = not os.path.exists(path)
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self._create_schema()
        if first_run:
            self._seed_demo_data()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------
    def _create_schema(self):
        c = self.conn.cursor()
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT
            );

            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_code TEXT UNIQUE NOT NULL,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                contact TEXT,
                email TEXT,
                start_hour INTEGER NOT NULL DEFAULT 9,
                end_hour INTEGER NOT NULL DEFAULT 17,
                consultation_fee REAL NOT NULL DEFAULT 500,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_code TEXT UNIQUE NOT NULL,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                age INTEGER,
                dob TEXT,
                gender TEXT,
                blood_group TEXT,
                contact TEXT,
                email TEXT,
                address TEXT,
                emergency_contact_name TEXT,
                emergency_contact_number TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS family_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                age INTEGER,
                relation TEXT
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
                doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
                family_member_id INTEGER REFERENCES family_members(id) ON DELETE SET NULL,
                for_name TEXT NOT NULL,
                appt_date TEXT NOT NULL,
                appt_hour INTEGER NOT NULL,
                reason TEXT,
                status TEXT NOT NULL DEFAULT 'Scheduled',
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
                doctor_id INTEGER REFERENCES doctors(id) ON DELETE SET NULL,
                appointment_id INTEGER REFERENCES appointments(id) ON DELETE SET NULL,
                record_date TEXT NOT NULL,
                symptoms TEXT,
                diagnosis TEXT,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medical_record_id INTEGER NOT NULL REFERENCES medical_records(id) ON DELETE CASCADE,
                medicine_name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                duration TEXT,
                instructions TEXT
            );

            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
                appointment_id INTEGER REFERENCES appointments(id) ON DELETE SET NULL,
                bill_date TEXT NOT NULL,
                total_amount REAL NOT NULL DEFAULT 0,
                paid INTEGER NOT NULL DEFAULT 0,
                payment_method TEXT
            );

            CREATE TABLE IF NOT EXISTS bill_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
                description TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_appt_doctor_date ON appointments(doctor_id, appt_date, appt_hour);
            CREATE INDEX IF NOT EXISTS idx_appt_patient ON appointments(patient_id);
            CREATE INDEX IF NOT EXISTS idx_records_patient ON medical_records(patient_id);
            CREATE INDEX IF NOT EXISTS idx_bills_patient ON bills(patient_id);
            """
        )
        self.conn.commit()

        # default admin account
        cur = self.conn.execute("SELECT COUNT(*) AS n FROM admins")
        if cur.fetchone()["n"] == 0:
            salt, h = hash_password(DEFAULT_ADMIN_PASS)
            self.conn.execute(
                "INSERT INTO admins (username, salt, password_hash, full_name) VALUES (?,?,?,?)",
                (DEFAULT_ADMIN_USER, salt, h, "System Administrator"),
            )
            self.conn.commit()

    def _seed_demo_data(self):
        """Populate a fresh database with a handful of doctors so the app
        is immediately demoable without manual setup."""
        demo_doctors = [
            ("Dr. Aanya Sharma", "Cardiology", "9810000001", "aanya.sharma@medcore.in", 9, 15, 800),
            ("Dr. Rohan Mehta", "Orthopedics", "9810000002", "rohan.mehta@medcore.in", 10, 18, 700),
            ("Dr. Kavita Nair", "Pediatrics", "9810000003", "kavita.nair@medcore.in", 9, 14, 600),
            ("Dr. Vikram Singh", "General Medicine", "9810000004", "vikram.singh@medcore.in", 11, 19, 500),
            ("Dr. Priya Iyer", "Dermatology", "9810000005", "priya.iyer@medcore.in", 10, 16, 650),
        ]
        for name, spec, contact, email, sh, eh, fee in demo_doctors:
            self.add_doctor(name, spec, "doctor123", contact, email, sh, eh, fee)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _next_code(self, table, code_col, prefix):
        cur = self.conn.execute(
            f"SELECT {code_col} FROM {table} WHERE {code_col} LIKE ? ORDER BY id DESC LIMIT 1",
            (prefix + "%",),
        )
        row = cur.fetchone()
        if not row:
            n = 1
        else:
            try:
                n = int(row[0][len(prefix):]) + 1
            except ValueError:
                n = 1
        return f"{prefix}{n:03d}"

    # ------------------------------------------------------------------
    # Admin
    # ------------------------------------------------------------------
    def verify_admin(self, username, password):
        row = self.conn.execute(
            "SELECT * FROM admins WHERE username = ?", (username,)
        ).fetchone()
        if not row:
            return False
        return verify_password(password, row["salt"], row["password_hash"])

    # ------------------------------------------------------------------
    # Doctors
    # ------------------------------------------------------------------
    def add_doctor(self, name, specialization, password, contact="", email="",
                    start_hour=9, end_hour=17, fee=500.0):
        code = self._next_code("doctors", "doctor_code", "DOC")
        salt, h = hash_password(password)
        cur = self.conn.execute(
            """INSERT INTO doctors
               (doctor_code, salt, password_hash, name, specialization, contact, email,
                start_hour, end_hour, consultation_fee, active, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,1,?)""",
            (code, salt, h, name, specialization, contact, email,
             start_hour, end_hour, fee, now_iso()),
        )
        self.conn.commit()
        return cur.lastrowid, code

    def update_doctor(self, doctor_id, **fields):
        if not fields:
            return
        cols = ", ".join(f"{k} = ?" for k in fields)
        vals = list(fields.values()) + [doctor_id]
        self.conn.execute(f"UPDATE doctors SET {cols} WHERE id = ?", vals)
        self.conn.commit()

    def set_doctor_active(self, doctor_id, active: bool):
        self.conn.execute("UPDATE doctors SET active = ? WHERE id = ?", (1 if active else 0, doctor_id))
        self.conn.commit()

    def get_doctors(self, active_only=False):
        q = "SELECT * FROM doctors"
        if active_only:
            q += " WHERE active = 1"
        q += " ORDER BY name"
        return self.conn.execute(q).fetchall()

    def get_doctor(self, doctor_id):
        return self.conn.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,)).fetchone()

    def verify_doctor(self, doctor_code, password):
        row = self.conn.execute(
            "SELECT * FROM doctors WHERE doctor_code = ? AND active = 1", (doctor_code,)
        ).fetchone()
        if not row:
            return None
        if verify_password(password, row["salt"], row["password_hash"]):
            return row
        return None

    # ------------------------------------------------------------------
    # Patients
    # ------------------------------------------------------------------
    def register_patient(self, full_name, age, dob, gender, blood_group, contact,
                          email, address, emergency_name, emergency_number, password):
        initials = "".join(ch for ch in full_name.upper() if ch.isalpha())[:3] or "PAT"
        code = self._next_code("patients", "patient_code", initials)
        salt, h = hash_password(password)
        cur = self.conn.execute(
            """INSERT INTO patients
               (patient_code, salt, password_hash, full_name, age, dob, gender, blood_group,
                contact, email, address, emergency_contact_name, emergency_contact_number, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (code, salt, h, full_name, age, dob, gender, blood_group, contact, email,
             address, emergency_name, emergency_number, now_iso()),
        )
        self.conn.commit()
        return cur.lastrowid, code

    def update_patient(self, patient_id, **fields):
        if not fields:
            return
        cols = ", ".join(f"{k} = ?" for k in fields)
        vals = list(fields.values()) + [patient_id]
        self.conn.execute(f"UPDATE patients SET {cols} WHERE id = ?", vals)
        self.conn.commit()

    def get_patients(self):
        return self.conn.execute("SELECT * FROM patients ORDER BY full_name").fetchall()

    def get_patient(self, patient_id):
        return self.conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()

    def get_patient_by_code(self, code):
        return self.conn.execute("SELECT * FROM patients WHERE patient_code = ?", (code,)).fetchone()

    def verify_patient(self, code, password):
        row = self.get_patient_by_code(code)
        if not row:
            return None
        if verify_password(password, row["salt"], row["password_hash"]):
            return row
        return None

    def search_patients(self, term):
        like = f"%{term}%"
        return self.conn.execute(
            """SELECT * FROM patients WHERE patient_code LIKE ? OR full_name LIKE ?
               OR contact LIKE ? OR email LIKE ? ORDER BY full_name""",
            (like, like, like, like),
        ).fetchall()

    # ------------------------------------------------------------------
    # Family members
    # ------------------------------------------------------------------
    def add_family_member(self, patient_id, name, age, relation):
        cur = self.conn.execute(
            "INSERT INTO family_members (patient_id, name, age, relation) VALUES (?,?,?,?)",
            (patient_id, name, age, relation),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_family_members(self, patient_id):
        return self.conn.execute(
            "SELECT * FROM family_members WHERE patient_id = ? ORDER BY name", (patient_id,)
        ).fetchall()

    # ------------------------------------------------------------------
    # Appointments
    # ------------------------------------------------------------------
    def count_slot(self, doctor_id, appt_date, appt_hour, exclude_id=None):
        q = """SELECT COUNT(*) AS n FROM appointments
               WHERE doctor_id = ? AND appt_date = ? AND appt_hour = ? AND status != 'Cancelled'"""
        params = [doctor_id, appt_date, appt_hour]
        if exclude_id:
            q += " AND id != ?"
            params.append(exclude_id)
        return self.conn.execute(q, params).fetchone()["n"]

    def slot_is_open(self, doctor_id, appt_date, appt_hour, exclude_id=None):
        return self.count_slot(doctor_id, appt_date, appt_hour, exclude_id) < MAX_SLOTS_PER_HOUR

    def book_appointment(self, patient_id, doctor_id, appt_date, appt_hour, reason,
                          for_name, family_member_id=None):
        if not self.slot_is_open(doctor_id, appt_date, appt_hour):
            raise ValueError("That time slot is already full. Please choose another.")
        cur = self.conn.execute(
            """INSERT INTO appointments
               (patient_id, doctor_id, family_member_id, for_name, appt_date, appt_hour,
                reason, status, created_at)
               VALUES (?,?,?,?,?,?,?, 'Scheduled', ?)""",
            (patient_id, doctor_id, family_member_id, for_name, appt_date, appt_hour,
             reason, now_iso()),
        )
        self.conn.commit()
        return cur.lastrowid

    def reschedule_appointment(self, appt_id, new_date, new_hour):
        appt = self.get_appointment(appt_id)
        if not appt:
            raise ValueError("Appointment not found.")
        if not self.slot_is_open(appt["doctor_id"], new_date, new_hour, exclude_id=appt_id):
            raise ValueError("That time slot is already full. Please choose another.")
        self.conn.execute(
            "UPDATE appointments SET appt_date = ?, appt_hour = ? WHERE id = ?",
            (new_date, new_hour, appt_id),
        )
        self.conn.commit()

    def cancel_appointment(self, appt_id):
        self.conn.execute("UPDATE appointments SET status = 'Cancelled' WHERE id = ?", (appt_id,))
        self.conn.commit()

    def complete_appointment(self, appt_id):
        self.conn.execute("UPDATE appointments SET status = 'Completed' WHERE id = ?", (appt_id,))
        self.conn.commit()

    def get_appointment(self, appt_id):
        return self.conn.execute("SELECT * FROM appointments WHERE id = ?", (appt_id,)).fetchone()

    def get_appointments_for_patient(self, patient_id):
        return self.conn.execute(
            """SELECT a.*, d.name AS doctor_name, d.specialization
               FROM appointments a JOIN doctors d ON a.doctor_id = d.id
               WHERE a.patient_id = ? ORDER BY a.appt_date DESC, a.appt_hour DESC""",
            (patient_id,),
        ).fetchall()

    def get_appointments_for_doctor(self, doctor_id, date_filter=None, status_filter=None):
        q = """SELECT a.*, p.full_name AS patient_full_name, p.patient_code
               FROM appointments a JOIN patients p ON a.patient_id = p.id
               WHERE a.doctor_id = ?"""
        params = [doctor_id]
        if date_filter:
            q += " AND a.appt_date = ?"
            params.append(date_filter)
        if status_filter:
            q += " AND a.status = ?"
            params.append(status_filter)
        q += " ORDER BY a.appt_date, a.appt_hour"
        return self.conn.execute(q, params).fetchall()

    def get_all_appointments(self, date_filter=None, doctor_filter=None, status_filter=None):
        q = """SELECT a.*, p.full_name AS patient_full_name, p.patient_code,
                      d.name AS doctor_name, d.specialization
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               JOIN doctors d ON a.doctor_id = d.id
               WHERE 1=1"""
        params = []
        if date_filter:
            q += " AND a.appt_date = ?"
            params.append(date_filter)
        if doctor_filter:
            q += " AND a.doctor_id = ?"
            params.append(doctor_filter)
        if status_filter:
            q += " AND a.status = ?"
            params.append(status_filter)
        q += " ORDER BY a.appt_date DESC, a.appt_hour DESC"
        return self.conn.execute(q, params).fetchall()

    def available_hours(self, doctor_id, appt_date):
        doc = self.get_doctor(doctor_id)
        if not doc:
            return []
        hours = []
        for h in range(doc["start_hour"], doc["end_hour"]):
            if self.slot_is_open(doctor_id, appt_date, h):
                hours.append(h)
        return hours

    # ------------------------------------------------------------------
    # Medical records & prescriptions
    # ------------------------------------------------------------------
    def add_medical_record(self, patient_id, doctor_id, appointment_id, symptoms,
                            diagnosis, notes, prescriptions=None):
        cur = self.conn.execute(
            """INSERT INTO medical_records
               (patient_id, doctor_id, appointment_id, record_date, symptoms, diagnosis, notes)
               VALUES (?,?,?,?,?,?,?)""",
            (patient_id, doctor_id, appointment_id, now_iso(), symptoms, diagnosis, notes),
        )
        record_id = cur.lastrowid
        for med in (prescriptions or []):
            self.conn.execute(
                """INSERT INTO prescriptions
                   (medical_record_id, medicine_name, dosage, frequency, duration, instructions)
                   VALUES (?,?,?,?,?,?)""",
                (record_id, med.get("name", ""), med.get("dosage", ""),
                 med.get("frequency", ""), med.get("duration", ""), med.get("instructions", "")),
            )
        self.conn.commit()
        return record_id

    def get_medical_records(self, patient_id):
        return self.conn.execute(
            """SELECT mr.*, d.name AS doctor_name FROM medical_records mr
               LEFT JOIN doctors d ON mr.doctor_id = d.id
               WHERE mr.patient_id = ? ORDER BY mr.record_date DESC""",
            (patient_id,),
        ).fetchall()

    def get_prescriptions(self, medical_record_id):
        return self.conn.execute(
            "SELECT * FROM prescriptions WHERE medical_record_id = ?", (medical_record_id,)
        ).fetchall()

    # ------------------------------------------------------------------
    # Billing
    # ------------------------------------------------------------------
    def create_bill(self, patient_id, appointment_id, items, payment_method=None, paid=False):
        total = sum(item["amount"] for item in items)
        cur = self.conn.execute(
            """INSERT INTO bills (patient_id, appointment_id, bill_date, total_amount, paid, payment_method)
               VALUES (?,?,?,?,?,?)""",
            (patient_id, appointment_id, now_iso(), total, 1 if paid else 0, payment_method),
        )
        bill_id = cur.lastrowid
        for item in items:
            self.conn.execute(
                "INSERT INTO bill_items (bill_id, description, amount) VALUES (?,?,?)",
                (bill_id, item["description"], item["amount"]),
            )
        self.conn.commit()
        return bill_id

    def mark_bill_paid(self, bill_id, payment_method="Cash"):
        self.conn.execute(
            "UPDATE bills SET paid = 1, payment_method = ? WHERE id = ?", (payment_method, bill_id)
        )
        self.conn.commit()

    def get_bills_for_patient(self, patient_id):
        return self.conn.execute(
            "SELECT * FROM bills WHERE patient_id = ? ORDER BY bill_date DESC", (patient_id,)
        ).fetchall()

    def get_all_bills(self):
        return self.conn.execute(
            """SELECT b.*, p.full_name AS patient_full_name, p.patient_code
               FROM bills b JOIN patients p ON b.patient_id = p.id
               ORDER BY b.bill_date DESC"""
        ).fetchall()

    def get_bill_items(self, bill_id):
        return self.conn.execute("SELECT * FROM bill_items WHERE bill_id = ?", (bill_id,)).fetchall()

    # ------------------------------------------------------------------
    # Dashboard / analytics
    # ------------------------------------------------------------------
    def stats_overview(self):
        c = self.conn
        total_patients = c.execute("SELECT COUNT(*) n FROM patients").fetchone()["n"]
        total_doctors = c.execute("SELECT COUNT(*) n FROM doctors WHERE active=1").fetchone()["n"]
        today = datetime.date.today().isoformat()
        today_appts = c.execute(
            "SELECT COUNT(*) n FROM appointments WHERE appt_date = ? AND status != 'Cancelled'",
            (today,),
        ).fetchone()["n"]
        pending_bills = c.execute("SELECT COUNT(*) n FROM bills WHERE paid = 0").fetchone()["n"]
        revenue_month = c.execute(
            "SELECT COALESCE(SUM(total_amount),0) s FROM bills WHERE paid = 1 AND bill_date >= ?",
            (datetime.date.today().replace(day=1).isoformat(),),
        ).fetchone()["s"]
        return {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "today_appts": today_appts,
            "pending_bills": pending_bills,
            "revenue_month": revenue_month,
        }

    def appointments_per_day(self, days=7):
        today = datetime.date.today()
        result = []
        for i in range(days - 1, -1, -1):
            d = (today - datetime.timedelta(days=i)).isoformat()
            n = self.conn.execute(
                "SELECT COUNT(*) n FROM appointments WHERE appt_date = ? AND status != 'Cancelled'",
                (d,),
            ).fetchone()["n"]
            result.append((d, n))
        return result

    def appointments_by_specialization(self):
        return self.conn.execute(
            """SELECT d.specialization AS spec, COUNT(*) AS n
               FROM appointments a JOIN doctors d ON a.doctor_id = d.id
               WHERE a.status != 'Cancelled'
               GROUP BY d.specialization ORDER BY n DESC"""
        ).fetchall()

    def close(self):
        self.conn.close()
