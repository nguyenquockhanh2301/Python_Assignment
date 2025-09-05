import mysql.connector
from datetime import datetime

# 1. Connection to database
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="medical_service"
    )

# 2. Add exactly 3 patients and 5 doctors
def add_patients_doctors():
    conn = get_connection()
    cur = conn.cursor()

    # Add 3 patients
    for i in range(3):
        print(f"\nEnter details for patient {i+1}:")
        name = input("Full name: ")
        dob = input("Date of birth (YYYY-MM-DD): ")
        gender = input("Gender: ")
        address = input("Address: ")
        phone = input("Phone number: ")
        email = input("Email: ")

        cur.execute("""
            INSERT INTO patients (full_name, date_of_birth, gender, address, phone_number, email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, dob, gender, address, phone, email))

    # Add 5 doctors
    for i in range(5):
        print(f"\nEnter details for doctor {i+1}:")
        name = input("Full name: ")
        spec = input("Specialization: ")
        phone = input("Phone number: ")
        email = input("Email: ")
        exp = input("Years of experience: ")

        cur.execute("""
            INSERT INTO doctors (full_name, specialization, phone_number, email, years_of_experience)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, spec, phone, email, exp))

    conn.commit()
    conn.close()
    print("✅ 3 patients and 5 doctors added successfully")

# 3. Add exactly 3 appointments
def add_appointments():
    conn = get_connection()
    cur = conn.cursor()

    for i in range(3):
        print(f"\nEnter appointment {i+1}:")
        patient_id = input("Patient ID: ")
        doctor_id = input("Doctor ID: ")
        date_str = input("Appointment date (YYYY-MM-DD HH:MM:SS): ")
        reason = input("Reason: ")
        status = input("Status (Pending/Done): ")

        try:
            appt_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            appt_date = datetime.now()

        cur.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (patient_id, doctor_id, appt_date, reason, status))

    conn.commit()
    conn.close()
    print("✅ 3 appointments added successfully")

# 4. Report
def report():
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT p.full_name, p.date_of_birth, p.gender, p.address,
               d.full_name, a.reason, a.appointment_date
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
    """
    cur.execute(query)
    rows = cur.fetchall()

    print("\n--- Report ---")
    print("No | Patient Name | Birthday | Gender | Address | Doctor | Reason | Date")
    for idx, row in enumerate(rows, start=1):
        print(f"{idx} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]}")
    conn.close()

# --- Main Menu ---
if __name__ == "__main__":
    while True:
        print("\n--- Assignment Strict Version ---")
        print("1. Add 3 Patients and 5 Doctors")
        print("2. Add 3 Appointments for 3 Patients")
        print("3. Show Report")
        print("0. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_patients_doctors()
        elif choice == "2":
            add_appointments()
        elif choice == "3":
            report()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("❌ Invalid choice")
