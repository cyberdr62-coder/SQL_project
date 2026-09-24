
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

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

class ClinicViewerApp(App):
    def build(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.executescript(SQL_SCRIPT)
        conn.commit()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]

        # حاوية رئيسية قابلة للتمرير الرأسي
        root_scroll = ScrollView(size_hint=(1, 1))
        main_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=25, padding=20)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        title = Label(
            text="قاعدة بيانات العيادة الطبية",
            size_hint_y=None,
            height=60,
            font_size='22sp',
            bold=True,
            color=(0.2, 0.7, 1, 1)
        )
        main_layout.add_widget(title)

        for table in tables:
            cursor.execute(f"SELECT * FROM {table};")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            t_label = Label(
                text=f"جدول: {table}",
                size_hint_y=None,
                height=40,
                font_size='18sp',
                bold=True,
                color=(0.3, 0.9, 0.5, 1)
            )
            main_layout.add_widget(t_label)

            # حاوية للتمرير الأفقي لكل جدول (يمين ويسار)
            table_h_scroll = ScrollView(size_hint=(1, None), height=260, do_scroll_x=True, do_scroll_y=True)

            num_cols = len(columns)
            col_width = 180
            total_width = max(num_cols * col_width, 600)

            grid = GridLayout(
                cols=num_cols,
                size_hint=(None, None),
                width=total_width,
                spacing=5
            )
            grid.bind(minimum_height=grid.setter('height'))

            for col in columns:
                lbl = Label(
                    text=str(col),
                    size_hint=(None, None),
                    size=(col_width, 40),
                    bold=True,
                    color=(1, 0.8, 0.2, 1)
                )
                grid.add_widget(lbl)

            for row in rows:
                for val in row:
                    cell_text = str(val) if val is not None else "NULL"
                    lbl = Label(
                        text=cell_text,
                        size_hint=(None, None),
                        size=(col_width, 35)
                    )
                    grid.add_widget(lbl)

            table_h_scroll.add_widget(grid)
            main_layout.add_widget(table_h_scroll)

        conn.close()
        root_scroll.add_widget(main_layout)
        return root_scroll

if __name__ == "__main__":
    ClinicViewerApp().run()
