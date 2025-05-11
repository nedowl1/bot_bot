import sqlite3
import os

# Удаляем файл базы данных, если он существует
if os.path.exists("db.db"):
    os.remove("db.db")
    print("Старый файл базы данных удалён.")

conn = sqlite3.connect("db.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    avatar TEXT,
    phone TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    description TEXT, -- Описание врача
    verification_docs TEXT, -- Документы для верификации
    verification_status TEXT DEFAULT 'pending', -- 'pending', 'verified', 'rejected'
    rating REAL DEFAULT 0.0, -- Средний рейтинг
    balance REAL DEFAULT 0.0, -- Для вывода денег
    experience INTEGER, -- Стаж работы (в годах)
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
print("Таблица doctors создана или уже существует.")

c.execute('''CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    avatar TEXT,
    phone TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
print("Таблица patients создана или уже существует.")

c.execute('''CREATE TABLE consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    description TEXT NOT NULL, -- Краткое описание запроса
    status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'completed', 'disputed'
    payment_status TEXT DEFAULT 'pending', -- 'pending', 'paid', 'refunded'
    total_price REAL NOT NULL, -- Сумма оплаты
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patients(id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(id)
)
''')
print("Таблица consultations создана или уже существует.")

c.execute('''CREATE TABLE chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    messages JSON NOT NULL, -- JSON-структура хранения сообщений
    last_message_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_open INTEGER DEFAULT 1, -- 1 = чат активен, 0 = закрыт
    FOREIGN KEY(consultation_id) REFERENCES consultations(id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(id),
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)
''')
print("Таблица chats создана или уже существует.")

c.execute('''CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    commission REAL DEFAULT 200.0,
    payment_provider TEXT NOT NULL, -- 'Stripe', 'CloudPayments'
    status TEXT DEFAULT 'pending', -- 'pending', 'completed', 'refunded'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(consultation_id) REFERENCES consultations(id),
    FOREIGN KEY(patient_id) REFERENCES patients(id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(id)
)''')
print("Таблица transactions создана или уже существует.")

c.execute('''CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5), -- Оценка пациента
    ai_rating REAL DEFAULT NULL, -- Оценка AI
    comments TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(doctor_id) REFERENCES doctors(id),
    FOREIGN KEY(patient_id) REFERENCES patients(id)
)''')
print("Таблица reviews создана или уже существует.")

c.execute('''CREATE TABLE specialisation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL, -- Название специальности
    name_ru TEXT, -- Название специальности на русском
    price REAL NOT NULL -- Цена консультации
)''')
print("Таблица specialisation создана или уже существует.")