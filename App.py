import sqlite3

DB_NAME = "clinic.db"

SQL_SCRIPT = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Patients (
    PatientID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientName TEXT NOT NULL,
    Gender TEXT,
    BirthDate TEXT,
    Phone TEXT,
    Address TEXT,
    BloodType TEXT,
    EmergencyContact TEXT,
    EmergencyPhone TEXT
);

CREATE TABLE IF NOT EXISTS Doctors (
    DoctorID INTEGER PRIMARY KEY AUTOINCREMENT,
    DoctorName TEXT NOT NULL,
    Specialty TEXT,
    Phone TEXT,
    Email TEXT,
    Address TEXT
);

CREATE TABLE IF NOT EXISTS Diagnoses (
    DiagnosisID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    DoctorID INTEGER NOT NULL,
    Diagnosis TEXT NOT NULL,
    DiagnosisDate TEXT NOT NULL,
    Symptoms TEXT,
    Notes TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Medicines (
    MedicineID INTEGER PRIMARY KEY AUTOINCREMENT,
    MedicineName TEXT NOT NULL,
    MedicineType TEXT,
    Manufacturer TEXT,
    Quantity INTEGER DEFAULT 0,
    UnitPrice REAL NOT NULL,
    ExpiryDate TEXT,
    Description TEXT
);

CREATE TABLE IF NOT EXISTS Treatments (
    TreatmentID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    DoctorID INTEGER NOT NULL,
    DiagnosisID INTEGER,
    TreatmentDate TEXT NOT NULL,
    TreatmentDescription TEXT,
    Notes TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE RESTRICT,
    FOREIGN KEY (DiagnosisID) REFERENCES Diagnoses(DiagnosisID) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Prescriptions (
    PrescriptionID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    DoctorID INTEGER NOT NULL,
    PrescriptionDate TEXT NOT NULL,
    Notes TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS PrescriptionDetails (
    DetailID INTEGER PRIMARY KEY AUTOINCREMENT,
    PrescriptionID INTEGER NOT NULL,
    MedicineID INTEGER NOT NULL,
    Dose TEXT,
    Frequency TEXT,
    Duration TEXT,
    Instructions TEXT,
    FOREIGN KEY (PrescriptionID) REFERENCES Prescriptions(PrescriptionID) ON DELETE CASCADE,
    FOREIGN KEY (MedicineID) REFERENCES Medicines(MedicineID) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Appointments (
    AppointmentID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    DoctorID INTEGER NOT NULL,
    AppointmentDate TEXT NOT NULL,
    AppointmentTime TEXT NOT NULL,
    Status TEXT DEFAULT 'Scheduled',
    Reason TEXT,
    Notes TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Payments (
    PaymentID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    PaymentDate TEXT NOT NULL,
    Amount REAL NOT NULL,
    PaymentType TEXT,
    Description TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE
);

INSERT INTO Doctors (DoctorName, Specialty, Phone, Email, Address) VALUES
('د. أحمد علي', 'باطنية', '0123456789', 'ahmed@hospital.com', 'الخرطوم'),
('د. سارة محمد', 'أطفال', '0987654321', 'sara@hospital.com', 'أم درمان');

INSERT INTO Patients (PatientName, Gender, BirthDate, Phone, Address, BloodType, EmergencyContact, EmergencyPhone) VALUES
('خالد إبراهيم', 'ذكر', '1995-04-12', '0911223344', 'الخرطوم', 'O+', 'محمد إبراهيم', '0922334455'),
('فاطمة حسن', 'أنثى', '2000-08-23', '0955667788', 'بحري', 'A+', 'حسن عثمان', '0966778899');

INSERT INTO Medicines (MedicineName, MedicineType, Manufacturer, Quantity, UnitPrice, ExpiryDate, Description) VALUES
('باراسيتامول 500 ملغ', 'حبوب', 'شركة الدواء', 100, 15.50, '2027-12-31', 'مسكن للآلام وخافض للحرارة'),
('أموكسيسيلين 250 ملغ', 'شراب', 'فارما', 50, 45.00, '2026-10-15', 'مضاد حيوي واسع المجال');

INSERT INTO Diagnoses (PatientID, DoctorID, Diagnosis, DiagnosisDate, Symptoms, Notes) VALUES
(1, 1, 'التهاب معدة حاد', '2026-03-01', 'ألم في البطن وغثيان', 'يحتاج متابعة بعد أسبوع');

INSERT INTO Treatments (PatientID, DoctorID, DiagnosisID, TreatmentDate, TreatmentDescription, Notes) VALUES
(1, 1, 1, '2026-03-01', 'حمية غذائية ومضادات حموضة', 'الالتزام بمواعيد الوجبات');

INSERT INTO Prescriptions (PatientID, DoctorID, PrescriptionDate, Notes) VALUES
(1, 1, '2026-03-01', 'وصفة أسبوعية');

INSERT INTO PrescriptionDetails (PrescriptionID, MedicineID, Dose, Frequency, Duration, Instructions) VALUES
(1, 1, 'حبة واحدة', '3 مرات يومياً', '5 أيام', 'بعد الأكل');

INSERT INTO Appointments (PatientID, DoctorID, AppointmentDate, AppointmentTime, Status, Reason, Notes) VALUES
(1, 1, '2026-03-10', '10:00', 'Scheduled', 'متابعة أسبوعية', 'فحص دوري');

INSERT INTO Payments (PatientID, PaymentDate, Amount, PaymentType, Description) VALUES
(1, '2026-03-01', 150.00, 'كاش', 'رسوم الكشف والعلاج');
"""

def print_table_grid(cursor, table_name):
    query = f"SELECT * FROM {table_name};"
    cursor.execute(query)
    headers = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    print("=" * 80)
    print(f"SQL QUERY: {query}")
    print("=" * 80)

    # حساب عرض كل عمود لتنسيق الجدول بدقة مثل واجهات قواعد البيانات
    str_rows = [[str(val) if val is not None else "NULL" for val in row] for row in rows]
    col_widths = [len(h) for h in headers]
    for row in str_rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(val))

    # طباعة رؤوس الأعمدة
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print(header_line)
    print(sep_line)

    if str_rows:
        for row in str_rows:
            print(" | ".join(row[i].ljust(col_widths[i]) for i in range(len(row))))
    else:
        print("(0 rows returned)")
    print()

def main():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # إنشاء الجداول وتعبئتها
        cursor.executescript(SQL_SCRIPT)
        conn.commit()
        print(">>> تم تجهيز وتعبئة قاعدة البيانات بنجاح.\n")

        # جلب جميع الجداول وتنفيذ SELECT * عليها تباعاً
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            print_table_grid(cursor, table)

        conn.close()
    except Exception as e:
        print("حدث خطأ:", e)

    input("\nاضغط Enter للخروج من البرنامج...")

if __name__ == "__main__":
    main()
