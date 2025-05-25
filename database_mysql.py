"""
Альтернативна реалізація для роботи з MySQL
"""

import mysql.connector
from mysql.connector import Error
import json
import hashlib
import datetime
from typing import List, Tuple, Optional, Dict
from config import config


class MySQLDatabaseManager:
    """Клас для управління MySQL базою даних"""

    def __init__(self):
        self.connection = None
        self.connect()
        self.init_database()

    def connect(self):
        """Підключення до MySQL"""
        try:
            mysql_config = config.DATABASE_CONFIG['mysql']
            self.connection = mysql.connector.connect(
                host=mysql_config['host'],
                port=mysql_config['port'],
                database=mysql_config['database'],
                user=mysql_config['user'],
                password=mysql_config['password'],
                charset=mysql_config['charset'],
                autocommit=True
            )
            print("Успішне підключення до MySQL")
        except Error as e:
            print(f"Помилка підключення до MySQL: {e}")
            # Fallback до SQLite
            import sqlite3
            self.connection = sqlite3.connect("informatics_trainer.db")

    def init_database(self):
        """Ініціалізація бази даних та створення таблиць"""
        if not self.connection:
            return

        cursor = self.connection.cursor()

        try:
            # Таблиця користувачів
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(64) NOT NULL,
                    email VARCHAR(100),
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_admin BOOLEAN DEFAULT FALSE,
                    last_login TIMESTAMP NULL,
                    login_attempts INT DEFAULT 0,
                    locked_until TIMESTAMP NULL
                )
            ''')

            # Таблиця категорій
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

            # Таблиця питань
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    category_id INT,
                    question_text TEXT NOT NULL,
                    question_type ENUM('multiple_choice', 'true_false', 'text_input') NOT NULL,
                    correct_answer TEXT NOT NULL,
                    options JSON,
                    difficulty INT DEFAULT 1,
                    explanation TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INT,
                    is_active BOOLEAN DEFAULT TRUE,
                    usage_count INT DEFAULT 0,
                    FOREIGN KEY (category_id) REFERENCES categories (id),
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')

            # Таблиця результатів тестування
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    category_id INT,
                    total_questions INT,
                    correct_answers INT,
                    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    time_spent INT,
                    difficulty_level INT DEFAULT 1,
                    score DECIMAL(5,2),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')

            # Таблиця детальних відповідей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS answer_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_result_id INT,
                    question_id INT,
                    user_answer TEXT,
                    is_correct BOOLEAN,
                    time_spent INT,
                    FOREIGN KEY (test_result_id) REFERENCES test_results (id),
                    FOREIGN KEY (question_id) REFERENCES questions (id)
                )
            ''')

            # Таблиця сесій користувачів
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    session_token VARCHAR(128),
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_date TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Таблиця логів системи
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    action VARCHAR(100),
                    details TEXT,
                    ip_address VARCHAR(45),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            self.connection.commit()
            print("Таблиці MySQL успішно створені")

            # Додаємо початкові дані
            self.populate_initial_data()

        except Error as e:
            print(f"Помилка створення таблиць MySQL: {e}")
            self.connection.rollback()

    def populate_initial_data(self):
        """Додавання початкових даних до MySQL бази"""
        cursor = self.connection.cursor()

        try:
            # Перевіряємо чи є дані
            cursor.execute("SELECT COUNT(*) FROM categories")
            result = cursor.fetchone()

            if result[0] == 0:
                # Додаємо категорії
                categories = [
                    ("Основи програмування", "Базові концепції програмування"),
                    ("Алгоритми та структури даних",
                     "Алгоритми сортування, пошуку, структури даних"),
                    ("Бази даних", "SQL, реляційні бази даних"),
                    ("Мережі та Інтернет", "Протоколи, архітектура мереж"),
                    ("Операційні системи", "Принципи роботи ОС"),
                    ("Інформаційна безпека", "Криптографія, захист інформації"),
                    ("Веб-технології", "HTML, CSS, JavaScript"),
                    ("Об'єктно-орієнтоване програмування",
                     "Класи, об'єкти, наслідування")
                ]

                cursor.executemany(
                    "INSERT INTO categories (name, description) VALUES (%s, %s)", categories)

                # Додаємо розширений набір питань
                questions = [
                    # Основи програмування (category_id = 1)
                    (1, "Що таке змінна в програмуванні?", "multiple_choice", "Іменована область пам'яті для зберігання даних",
                     '["Іменована область пам\'яті для зберігання даних", "Функція для обчислень", "Цикл виконання", "Умовний оператор"]', 1,
                     "Змінна - це іменована область пам'яті, яка використовується для зберігання даних"),

                    (1, "Python є інтерпретованою мовою програмування", "true_false", "True", None, 1,
                     "Python дійсно є інтерпретованою мовою програмування"),

                    (1, "Який оператор використовується для присвоєння в Python?", "text_input", "=", None, 1,
                     "Оператор = використовується для присвоєння значень змінним"),

                    (1, "Що виведе код: print(2 ** 3)?", "multiple_choice", "8",
                     '["6", "8", "9", "16"]', 2,
                     "Оператор ** означає піднесення до степеня, тому 2**3 = 8"),

                    (1, "Які з наступних є коментарями в Python?", "multiple_choice", "# Це коментар",
                     '["# Це коментар", "// Це коментар", "/* Це коментар */", "<!-- Це коментар -->"]', 1,
                     "В Python коментарі починаються з символу #"),

                    # Алгоритми та структури даних (category_id = 2)
                    (2, "Яка складність алгоритму бульбашкового сортування?", "multiple_choice", "O(n²)",
                     '["O(n)", "O(n²)", "O(log n)", "O(n log n)"]', 2,
                     "Бульбашкове сортування має квадратичну складність O(n²)"),

                    (2, "Стек працює за принципом LIFO", "true_false", "True", None, 2,
                     "LIFO (Last In, First Out) - останній прийшов, перший пішов"),

                    (2, "Яка структура даних використовується для реалізації рекурсії?", "multiple_choice", "Стек",
                     '["Черга", "Стек", "Список", "Дерево"]', 2,
                     "Рекурсія використовує стек викликів для збереження контексту функцій"),

                    (2, "Бінарний пошук працює тільки з відсортованими масивами", "true_false", "True", None, 2,
                     "Бінарний пошук вимагає відсортованого масиву для коректної роботи"),

                    (2, "Яка складність пошуку в хеш-таблиці в середньому випадку?", "multiple_choice", "O(1)",
                     '["O(1)", "O(log n)", "O(n)", "O(n²)"]', 3,
                     "Хеш-таблиця забезпечує константний час пошуку O(1) в середньому випадку"),

                    # Бази даних (category_id = 3)
                    (3, "Що означає SQL?", "text_input", "Structured Query Language", None, 1,
                     "SQL - Structured Query Language, мова структурованих запитів"),

                    (3, "Який оператор використовується для вибірки даних?", "multiple_choice", "SELECT",
                     '["INSERT", "SELECT", "UPDATE", "DELETE"]', 1,
                     "SELECT використовується для вибірки даних з таблиць"),

                    (3, "Первинний ключ може містити NULL значення", "true_false", "False", None, 2,
                     "Первинний ключ не може містити NULL значення та повинен бути унікальним"),

                    (3, "Яка команда використовується для створення нової таблиці?", "multiple_choice", "CREATE TABLE",
                     '["CREATE TABLE", "NEW TABLE", "ADD TABLE", "MAKE TABLE"]', 1,
                     "CREATE TABLE використовується для створення нових таблиць"),

                    (3, "Що таке нормалізація бази даних?", "multiple_choice", "Процес організації даних для зменшення надмірності",
                     '["Процес організації даних для зменшення надмірності", "Процес видалення даних", "Процес шифрування даних", "Процес резервного копіювання"]', 3,
                     "Нормалізація - це процес структурування бази даних для зменшення надмірності та покращення цілісності"),

                    # Мережі та Інтернет (category_id = 4)
                    (4, "HTTP працює на якому рівні моделі OSI?", "multiple_choice", "Прикладному",
                     '["Фізичному", "Канальному", "Мережевому", "Прикладному"]', 2,
                     "HTTP працює на прикладному (7-му) рівні моделі OSI"),

                    (4, "IP-адреса складається з 4 октетів", "true_false", "True", None, 1,
                     "IPv4 адреса дійсно складається з 4 октетів по 8 біт кожен"),

                    (4, "Який протокол використовується для надійної передачі даних?", "multiple_choice", "TCP",
                     '["UDP", "TCP", "ICMP", "ARP"]', 2,
                     "TCP (Transmission Control Protocol) забезпечує надійну передачу даних"),

                    (4, "Що означає DNS?", "text_input", "Domain Name System", None, 2,
                     "DNS - Domain Name System, система доменних імен"),

                    (4, "HTTPS використовує шифрування", "true_false", "True", None, 2,
                     "HTTPS використовує SSL/TLS шифрування для безпечної передачі даних"),

                    # Операційні системи (category_id = 5)
                    (5, "Що таке процес в ОС?", "multiple_choice", "Програма в стані виконання",
                     '["Файл на диску", "Програма в стані виконання", "Системний виклик", "Драйвер пристрою"]', 2,
                     "Процес - це програма, яка завантажена в пам'ять і виконується"),

                    (5, "Deadlock може виникнути при роботі з ресурсами", "true_false", "True", None, 3,
                     "Deadlock (взаємне блокування) виникає коли процеси чекають один одного"),

                    (5, "Яка команда в Linux показує запущені процеси?", "multiple_choice", "ps",
                     '["ls", "ps", "cd", "mkdir"]', 2,
                     "Команда ps показує список запущених процесів"),

                    (5, "Віртуальна пам'ять дозволяє використовувати більше пам'яті ніж фізично доступно", "true_false", "True", None, 2,
                     "Віртуальна пам'ять використовує диск як розширення оперативної пам'яті"),

                    # Інформаційна безпека (category_id = 6)
                    (6, "Що таке хешування?", "multiple_choice", "Перетворення даних у фіксований розмір",
                     '["Шифрування даних", "Перетворення даних у фіксований розмір", "Стиснення файлів", "Резервне копіювання"]', 2,
                     "Хешування - це перетворення вхідних даних у рядок фіксованого розміру"),

                    (6, "Симетричне шифрування використовує один ключ для шифрування та розшифрування", "true_false", "True", None, 2,
                     "При симетричному шифруванні один і той же ключ використовується для обох операцій"),

                    (6, "Що таке фішинг?", "multiple_choice", "Спроба отримати конфіденційну інформацію обманним шляхом",
                     '["Вірус", "Спроба отримати конфіденційну інформацію обманним шляхом", "Тип шифрування", "Мережевий протокол"]', 2,
                     "Фішинг - це соціальна інженерія для крадіжки особистих даних"),

                    (6, "Яка довжина ключа вважається безпечною для AES?", "multiple_choice", "256 біт",
                     '["64 біт", "128 біт", "256 біт", "512 біт"]', 3,
                     "AES-256 вважається найбільш безпечним варіантом"),
                ]

                for q in questions:
                    cursor.execute('''
                        INSERT INTO questions (category_id, question_text, question_type, correct_answer, options, difficulty, explanation)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', q)

                # Створюємо адміністратора
                admin_password = hashlib.sha256(
                    "admin123".encode()).hexdigest()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, is_admin)
                    VALUES (%s, %s, %s, %s)
                ''', ("admin", admin_password, "admin@example.com", True))

                # Створюємо тестового користувача
                test_password = hashlib.sha256("test123".encode()).hexdigest()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, is_admin)
                    VALUES (%s, %s, %s, %s)
                ''', ("test_user", test_password, "test@example.com", False))

            self.connection.commit()
            print("Початкові дані MySQL успішно додані")

        except Error as e:
            print(f"Помилка додавання початкових даних MySQL: {e}")
            self.connection.rollback()

    def close_connection(self):
        """Закриття з'єднання з базою даних"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("З'єднання з MySQL закрито")
