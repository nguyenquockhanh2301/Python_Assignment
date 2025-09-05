#!/usr/bin/env python3
# medical_service.py (Flexible version)
# - Add any number of patients/doctors/appointments (type 'q' to stop)
# - Show report and today's appointments
# Works with XAMPP MySQL (default user root, no password)

import mysql.connector
from datetime import datetime, date

# -----------------------------
# DB Connection
# -----------------------------
def get_connection():
    """
    Create and return a MySQL connection.
    Adjust user/password/host if your setup differs.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="medical_service",
    )

# -----------------------------
# Helpers
# -----------------------------
def _nonempty_input(prompt: str) -> str:
    """Ask until user gives a non-empty string (cannot be just spaces)."""
    while True:
        s = input(prompt).strip()
        if s == "":
            print("This field is required. Please enter a value.")
            continue
        return s

def _optional_input(prompt: str) -> str:
    """Allow empty (optional) field."""
    return input(prompt).strip()

def _parse_datetime(s: str) -> datetime:
    """Try several formats; default to now() if invalid or empty."""
    s = (s or "").strip()
    if not s:
        return datetime.now()
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",  # if date only, default time 09:00
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            if fmt == "%Y-%m-%d":
                dt = dt.replace(hour=9, minute=0, second=0)
            return dt
        except ValueError:
            pass
    print("Invalid date/time format. Using current date/time instead.")
    return datetime.now()

def _select_exists(cur, table: str, id_field: str, id_value: int) -> bool:
    cur.execute(f"SELECT EXISTS(SELECT 1 FROM {table} WHERE {id_field} = %s)", (id_value,))
    return cur.fetchone()[0] == 1

# -----------------------------
# Core: Patients
# -----------------------------
def list_patients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT patient_id, full_name, date_of_birth, gender, address
        FROM patients
        ORDER BY patient_id
    """)
    rows = cur.fetchall()
    print("\nPatients:")
    print("ID | Full Name | DOB | Gender | Address")
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")
    cur.close()
    conn.close()

def add_patients():
    print("\nAdd Patients (type 'q' at Full name to stop)")
    conn = get_connection()
    cur = conn.cursor()
    i = 1
    while True:
        name = input(f"\nFull name for patient {i} (or 'q' to stop): ").strip()
        if name.lower() == "q":
            break
        if name == "":
            print("Name is required.")
            continue
        dob = _nonempty_input("Date of birth (YYYY-MM-DD): ")
        gender = _nonempty_input("Gender: ")
        address = _nonempty_input("Address: ")
        phone = _optional_input("Phone number (optional): ")
        email = _optional_input("Email (optional): ")
        cur.execute(
            """
            INSERT INTO patients (full_name, date_of_birth, gender, address, phone_number, email)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, dob, gender, address, phone, email),
        )
        conn.commit()
        print("✓ Patient added.")
        i += 1
    cur.close()
    conn.close()
    print("Done adding patients.")

# -----------------------------
# Core: Doctors
# -----------------------------
def list_doctors():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT doctor_id, full_name, specialization
        FROM doctors
        ORDER BY doctor_id
    """)
    rows = cur.fetchall()
    print("\nDoctors:")
    print("ID | Full Name | Specialization")
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]}")
    cur.close()
    conn.close()

def add_doctors():
    print("\nAdd Doctors (type 'q' at Full name to stop)")
    conn = get_connection()
    cur = conn.cursor()
    i = 1
    while True:
        name = input(f"\nFull name for doctor {i} (or 'q' to stop): ").strip()
        if name.lower() == "q":
            break
        if name == "":
            print("Name is required.")
            continue
        spec = _nonempty_input("Specialization: ")
        phone = _optional_input("Phone number (optional): ")
        email = _optional_input("Email (optional): ")
        exp = _optional_input("Years of experience (optional number): ")
        exp_val = int(exp) if exp.isdigit() else None
        cur.execute(
            """
            INSERT INTO doctors (full_name, specialization, phone_number, email, years_of_experience)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, spec, phone, email, exp_val),
        )
        conn.commit()
        print("✓ Doctor added.")
        i += 1
    cur.close()
    conn.close()
    print("Done adding doctors.")

# -----------------------------
# Core: Appointments
# -----------------------------
def add_appointments():
    print("\nAdd Appointments (type 'q' for Patient ID to stop)")
    # Show lists to help user pick IDs
    list_patients()
    list_doctors()

    conn = get_connection()
    cur = conn.cursor()
    i = 1
    while True:
        raw_pid = input(f"\nPatient ID for appointment {i} (or 'q' to stop): ").strip().lower()
        if raw_pid == "q":
            break
        if not raw_pid.isdigit():
            print("Please enter a numeric Patient ID.")
            continue
        patient_id = int(raw_pid)

        if not _select_exists(cur, "patients", "patient_id", patient_id):
            print("Patient ID not found. Use 'List Patients' to see valid IDs.")
            continue

        raw_did = _nonempty_input("Doctor ID: ")
        if not raw_did.isdigit():
            print("Please enter a numeric Doctor ID.")
            continue
        doctor_id = int(raw_did)

        if not _select_exists(cur, "doctors", "doctor_id", doctor_id):
            print("Doctor ID not found. Use 'List Doctors' to see valid IDs.")
            continue

        date_str = _optional_input("Appointment date (YYYY-MM-DD HH:MM:SS) [Enter for now]: ")
        appt_dt = _parse_datetime(date_str)
        reason = _optional_input("Reason (optional): ")
        status = _optional_input("Status (Pending/Done) [default Pending]: ")
        status = status if status else "Pending"

        cur.execute(
            """
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (patient_id, doctor_id, appt_dt, reason, status),
        )
        conn.commit()
        print("✓ Appointment added.")
        i += 1
    cur.close()
    conn.close()
    print("Done adding appointments.")

# -----------------------------
# Reports
# -----------------------------
def report():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.full_name, p.date_of_birth, p.gender, p.address,
               d.full_name, a.reason, a.appointment_date
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_date DESC, a.appointment_id DESC
        """
    )
    rows = cur.fetchall()
    print("\n--- Report ---")
    print("No | Patient Name | Birthday | Gender | Address | Doctor | Reason | Date/Time")
    for idx, row in enumerate(rows, start=1):
        print(f"{idx} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]}")
    cur.close()
    conn.close()

def today_appointments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.address, p.full_name, p.date_of_birth, p.gender,
               d.full_name, a.status, a.reason, a.appointment_date
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE DATE(a.appointment_date) = CURDATE()
        ORDER BY a.appointment_date
        """
    )
    rows = cur.fetchall()
    print("\n--- Today's Appointments ---")
    print("Address | No | Patient Name | Birthday | Gender | Doctor | Status | Note | Time")
    for idx, r in enumerate(rows, start=1):
        # r: address, patient_name, dob, gender, doctor_name, status, reason, appt_dt
        print(f"{r[0]} | {idx} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7].strftime('%H:%M:%S')}")
    cur.close()
    conn.close()

# -----------------------------
# Menu
# -----------------------------
def menu():
    while True:
        print("\n=== Medical Service (Flexible) ===")
        print("1. Add Patients")
        print("2. Add Doctors")
        print("3. Add Appointments")
        print("4. Show Report")
        print("5. Show Today's Appointments")
        print("6. List Patients (IDs)")
        print("7. List Doctors (IDs)")
        print("0. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            add_patients()
        elif choice == "2":
            add_doctors()
        elif choice == "3":
            add_appointments()
        elif choice == "4":
            report()
        elif choice == "5":
            today_appointments()
        elif choice == "6":
            list_patients()
        elif choice == "7":
            list_doctors()
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    try:
        menu()
    except mysql.connector.Error as err:
        print(f"MySQL error: {err}")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
