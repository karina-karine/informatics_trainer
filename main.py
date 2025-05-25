import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import hashlib
import datetime
import json
import random
from typing import Dict, List, Tuple, Optional


class DatabaseManager:
    """Клас для управління базою даних"""

    def __init__(self, db_name: str = "informatics_trainer.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Ініціалізація бази даних та створення таблиць"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Таблиця користувачів
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE
            )
        ''')

        # Таблиця категорій
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        ''')

        # Таблиця питань
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL, -- 'multiple_choice', 'true_false', 'text_input'
                correct_answer TEXT NOT NULL,
                options TEXT, -- JSON для варіантів відповідей
                difficulty INTEGER DEFAULT 1, -- 1-легко, 2-середньо, 3-важко
                explanation TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')

        # Таблиця результатів тестування
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category_id INTEGER,
                total_questions INTEGER,
                correct_answers INTEGER,
                test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                time_spent INTEGER, -- в секундах
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')

        # Таблиця детальних відповідей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answer_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_result_id INTEGER,
                question_id INTEGER,
                user_answer TEXT,
                is_correct BOOLEAN,
                time_spent INTEGER,
                FOREIGN KEY (test_result_id) REFERENCES test_results (id),
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
        ''')

        conn.commit()
        conn.close()

        # Додаємо початкові дані
        self.populate_initial_data()

    def populate_initial_data(self):
        """Додавання початкових даних до бази"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Перевіряємо чи є дані
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            # Додаємо категорії
            categories = [
                ("Основи програмування", "Базові концепції програмування"),
                ("Алгоритми та структури даних",
                 "Алгоритми сортування, пошуку, структури даних"),
                ("Бази даних", "SQL, реляційні бази даних"),
                ("Мережі та Інтернет", "Протоколи, архітектура мереж"),
                ("Операційні системи", "Принципи роботи ОС"),
                ("Інформаційна безпека", "Криптографія, захист інформації")
            ]

            cursor.executemany(
                "INSERT INTO categories (name, description) VALUES (?, ?)", categories)

            # Додаємо питання
            questions = [
                # Основи програмування
                (1, "Що таке змінна в програмуванні?", "multiple_choice", "Іменована область пам'яті для зберігання даних",
                 '["Іменована область пам\'яті для зберігання даних", "Функція для обчислень", "Цикл виконання", "Умовний оператор"]', 1,
                 "Змінна - це іменована область пам'яті, яка використовується для зберігання даних"),

                (1, "Python є інтерпретованою мовою програмування", "true_false", "True", None, 1,
                 "Python дійсно є інтерпретованою мовою програмування"),

                (1, "Який оператор використовується для присвоєння в Python?", "text_input", "=", None, 1,
                 "Оператор = використовується для присвоєння значень змінним"),

                # Алгоритми
                (2, "Яка складність алгоритму бульбашкового сортування?", "multiple_choice", "O(n²)",
                 '["O(n)", "O(n²)", "O(log n)", "O(n log n)"]', 2,
                 "Бульбашкове сортування має квадратичну складність O(n²)"),

                (2, "Стек працює за принципом LIFO", "true_false", "True", None, 2,
                 "LIFO (Last In, First Out) - останній прийшов, перший пішов"),

                # Бази даних
                (3, "Що означає SQL?", "text_input", "Structured Query Language", None, 1,
                 "SQL - Structured Query Language, мова структурованих запитів"),

                (3, "Який оператор використовується для вибірки даних?", "multiple_choice", "SELECT",
                 '["INSERT", "SELECT", "UPDATE", "DELETE"]', 1,
                 "SELECT використовується для вибірки даних з таблиць"),

                # Мережі
                (4, "HTTP працює на якому рівні моделі OSI?", "multiple_choice", "Прикладному",
                 '["Фізичному", "Канальному", "Мережевому", "Прикладному"]', 2,
                 "HTTP працює на прикладному (7-му) рівні моделі OSI"),

                (4, "IP-адреса складається з 4 октетів", "true_false", "True", None, 1,
                 "IPv4 адреса дійсно складається з 4 октетів по 8 біт кожен"),

                # Операційні системи
                (5, "Що таке процес в ОС?", "multiple_choice", "Програма в стані виконання",
                 '["Файл на диску", "Програма в стані виконання", "Системний виклик", "Драйвер пристрою"]', 2,
                 "Процес - це програма, яка завантажена в пам'ять і виконується"),

                # Інформаційна безпека
                (6, "Що таке хешування?", "multiple_choice", "Перетворення даних у фіксований розмір",
                 '["Шифрування даних", "Перетворення даних у фіксований розмір", "Стиснення файлів", "Резервне копіювання"]', 2,
                 "Хешування - це перетворення вхідних даних у рядок фіксованого розміру")
            ]

            for q in questions:
                cursor.execute('''
                    INSERT INTO questions (category_id, question_text, question_type, correct_answer, options, difficulty, explanation)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', q)

            # Створюємо адміністратора
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, is_admin)
                VALUES (?, ?, ?, ?)
            ''', ("admin", admin_password, "admin@example.com", True))

        conn.commit()
        conn.close()


class User:
    """Клас для представлення користувача"""

    def __init__(self, user_id: int, username: str, email: str = "", is_admin: bool = False):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.is_admin = is_admin


class Question:
    """Клас для представлення питання"""

    def __init__(self, question_id: int, category_id: int, question_text: str,
                 question_type: str, correct_answer: str, options: List[str] = None,
                 difficulty: int = 1, explanation: str = ""):
        self.question_id = question_id
        self.category_id = category_id
        self.question_text = question_text
        self.question_type = question_type
        self.correct_answer = correct_answer
        self.options = options or []
        self.difficulty = difficulty
        self.explanation = explanation


class AuthenticationManager:
    """Клас для управління автентифікацією"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.current_user: Optional[User] = None

    def register_user(self, username: str, password: str, email: str = "") -> bool:
        """Реєстрація нового користувача"""
        try:
            conn = sqlite3.connect(self.db_manager.db_name)
            cursor = conn.cursor()

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (username, password_hash, email))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def login_user(self, username: str, password: str) -> bool:
        """Авторизація користувача"""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('''
            SELECT id, username, email, is_admin
            FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))

        result = cursor.fetchone()
        conn.close()

        if result:
            self.current_user = User(
                result[0], result[1], result[2], bool(result[3]))
            return True
        return False

    def logout_user(self):
        """Вихід користувача"""
        self.current_user = None


class TestManager:
    """Клас для управління тестуванням"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.current_questions: List[Question] = []
        self.current_question_index = 0
        self.user_answers: List[str] = []
        self.start_time = None
        self.question_start_time = None

    def get_categories(self) -> List[Tuple[int, str, str]]:
        """Отримання списку категорій"""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, description FROM categories")
        categories = cursor.fetchall()

        conn.close()
        return categories

    def start_test(self, category_id: int, num_questions: int = 10) -> bool:
        """Початок тестування"""
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, category_id, question_text, question_type, correct_answer, options, difficulty, explanation
            FROM questions
            WHERE category_id = ?
            ORDER BY RANDOM()
            LIMIT ?
        ''', (category_id, num_questions))

        questions_data = cursor.fetchall()
        conn.close()

        if not questions_data:
            return False

        self.current_questions = []
        for q_data in questions_data:
            options = json.loads(q_data[5]) if q_data[5] else []
            question = Question(q_data[0], q_data[1], q_data[2],
                                q_data[3], q_data[4], options, q_data[6], q_data[7])
            self.current_questions.append(question)

        self.current_question_index = 0
        self.user_answers = []
        self.start_time = datetime.datetime.now()
        self.question_start_time = datetime.datetime.now()

        return True

    def get_current_question(self) -> Optional[Question]:
        """Отримання поточного питання"""
        if 0 <= self.current_question_index < len(self.current_questions):
            return self.current_questions[self.current_question_index]
        return None

    def submit_answer(self, answer: str) -> bool:
        """Подача відповіді на поточне питання"""
        if self.current_question_index < len(self.current_questions):
            self.user_answers.append(answer)
            self.current_question_index += 1
            self.question_start_time = datetime.datetime.now()
            return True
        return False

    def finish_test(self, user_id: int) -> Dict:
        """Завершення тестування та збереження результатів"""
        if not self.current_questions:
            return {}

        end_time = datetime.datetime.now()
        total_time = int((end_time - self.start_time).total_seconds())

        correct_count = 0
        for i, question in enumerate(self.current_questions):
            if i < len(self.user_answers):
                user_answer = self.user_answers[i].strip().lower()
                correct_answer = question.correct_answer.strip().lower()

                if question.question_type == "true_false":
                    if user_answer in ["true", "так", "1"] and correct_answer in ["true", "так", "1"]:
                        correct_count += 1
                    elif user_answer in ["false", "ні", "0"] and correct_answer in ["false", "ні", "0"]:
                        correct_count += 1
                else:
                    if user_answer == correct_answer:
                        correct_count += 1

        # Збереження результатів в базу
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO test_results (user_id, category_id, total_questions, correct_answers, time_spent)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, self.current_questions[0].category_id, len(self.current_questions), correct_count, total_time))

        test_result_id = cursor.lastrowid

        # Збереження детальних відповідей
        for i, question in enumerate(self.current_questions):
            if i < len(self.user_answers):
                user_answer = self.user_answers[i]
                is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()

                cursor.execute('''
                    INSERT INTO answer_details (test_result_id, question_id, user_answer, is_correct, time_spent)
                    VALUES (?, ?, ?, ?, ?)
                ''', (test_result_id, question.question_id, user_answer, is_correct, 30))

        conn.commit()
        conn.close()

        return {
            'total_questions': len(self.current_questions),
            'correct_answers': correct_count,
            'percentage': round((correct_count / len(self.current_questions)) * 100, 2),
            'time_spent': total_time
        }


class InformaticsTrainerGUI:
    """Головний клас графічного інтерфейсу"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Тренажер з Інформатики")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')

        # Ініціалізація компонентів
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthenticationManager(self.db_manager)
        self.test_manager = TestManager(self.db_manager)

        # Стилі
        self.setup_styles()

        # Показуємо екран входу
        self.show_login_screen()

    def setup_styles(self):
        """Налаштування стилів інтерфейсу"""
        style = ttk.Style()
        style.theme_use('clam')

        # Кольорова схема
        style.configure('Title.TLabel', font=(
            'Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Heading.TLabel', font=(
            'Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Custom.TButton', font=('Arial', 10))
        style.configure('Success.TLabel', foreground='green',
                        background='#f0f0f0')
        style.configure('Error.TLabel', foreground='red', background='#f0f0f0')

    def clear_window(self):
        """Очищення вікна"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        """Екран входу/реєстрації"""
        self.clear_window()

        # Головний фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')

        # Заголовок
        title_label = ttk.Label(
            main_frame, text="Тренажер з Інформатики", style='Title.TLabel')
        title_label.pack(pady=(0, 30))

        # Фрейм для форми входу
        login_frame = ttk.LabelFrame(
            main_frame, text="Вхід в систему", padding="20")
        login_frame.pack(pady=10, padx=50, fill='x')

        # Поля входу
        ttk.Label(login_frame, text="Ім'я користувача:").pack(anchor='w')
        self.username_entry = ttk.Entry(login_frame, width=30)
        self.username_entry.pack(pady=(0, 10), fill='x')

        ttk.Label(login_frame, text="Пароль:").pack(anchor='w')
        self.password_entry = ttk.Entry(login_frame, width=30, show="*")
        self.password_entry.pack(pady=(0, 10), fill='x')

        # Кнопки
        button_frame = ttk.Frame(login_frame)
        button_frame.pack(pady=10, fill='x')

        ttk.Button(button_frame, text="Увійти", command=self.login,
                   style='Custom.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Реєстрація", command=self.show_register_screen,
                   style='Custom.TButton').pack(side='left')

        # Повідомлення
        self.message_label = ttk.Label(
            login_frame, text="", style='Error.TLabel')
        self.message_label.pack(pady=10)

        # Демо-дані
        demo_frame = ttk.LabelFrame(
            main_frame, text="Демо-доступ", padding="10")
        demo_frame.pack(pady=10, padx=50, fill='x')

        ttk.Label(demo_frame, text="Адміністратор: admin / admin123").pack()
        ttk.Button(demo_frame, text="Увійти як адмін",
                   command=self.demo_admin_login).pack(pady=5)

        # Фокус на поле вводу
        self.username_entry.focus()

        # Обробка Enter
        self.root.bind('<Return>', lambda e: self.login())

    def show_register_screen(self):
        """Екран реєстрації"""
        self.clear_window()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')

        title_label = ttk.Label(
            main_frame, text="Реєстрація нового користувача", style='Title.TLabel')
        title_label.pack(pady=(0, 30))

        register_frame = ttk.LabelFrame(
            main_frame, text="Дані користувача", padding="20")
        register_frame.pack(pady=10, padx=50, fill='x')

        # Поля реєстрації
        ttk.Label(register_frame, text="Ім'я користувача:").pack(anchor='w')
        self.reg_username_entry = ttk.Entry(register_frame, width=30)
        self.reg_username_entry.pack(pady=(0, 10), fill='x')

        ttk.Label(register_frame, text="Пароль:").pack(anchor='w')
        self.reg_password_entry = ttk.Entry(register_frame, width=30, show="*")
        self.reg_password_entry.pack(pady=(0, 10), fill='x')

        ttk.Label(register_frame, text="Підтвердження паролю:").pack(anchor='w')
        self.reg_confirm_entry = ttk.Entry(register_frame, width=30, show="*")
        self.reg_confirm_entry.pack(pady=(0, 10), fill='x')

        ttk.Label(register_frame, text="Email (необов'язково):").pack(
            anchor='w')
        self.reg_email_entry = ttk.Entry(register_frame, width=30)
        self.reg_email_entry.pack(pady=(0, 10), fill='x')

        # Кнопки
        button_frame = ttk.Frame(register_frame)
        button_frame.pack(pady=10, fill='x')

        ttk.Button(button_frame, text="Зареєструватися",
                   command=self.register).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Назад",
                   command=self.show_login_screen).pack(side='left')

        # Повідомлення
        self.reg_message_label = ttk.Label(register_frame, text="")
        self.reg_message_label.pack(pady=10)

        self.reg_username_entry.focus()

    def login(self):
        """Обробка входу"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.message_label.config(
                text="Заповніть всі поля", style='Error.TLabel')
            return

        if self.auth_manager.login_user(username, password):
            self.show_main_menu()
        else:
            self.message_label.config(
                text="Невірне ім'я користувача або пароль", style='Error.TLabel')

    def demo_admin_login(self):
        """Демо-вхід адміністратора"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.insert(0, "admin")
        self.password_entry.insert(0, "admin123")
        self.login()

    def register(self):
        """Обробка реєстрації"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get().strip()
        confirm = self.reg_confirm_entry.get().strip()
        email = self.reg_email_entry.get().strip()

        if not username or not password:
            self.reg_message_label.config(
                text="Заповніть обов'язкові поля", style='Error.TLabel')
            return

        if password != confirm:
            self.reg_message_label.config(
                text="Паролі не співпадають", style='Error.TLabel')
            return

        if len(password) < 6:
            self.reg_message_label.config(
                text="Пароль повинен містити мінімум 6 символів", style='Error.TLabel')
            return

        if self.auth_manager.register_user(username, password, email):
            self.reg_message_label.config(
                text="Реєстрація успішна! Тепер ви можете увійти", style='Success.TLabel')
            self.root.after(2000, self.show_login_screen)
        else:
            self.reg_message_label.config(
                text="Користувач з таким ім'ям вже існує", style='Error.TLabel')

    def show_main_menu(self):
        """Головне меню"""
        self.clear_window()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')

        # Заголовок з привітанням
        welcome_text = f"Вітаємо, {self.auth_manager.current_user.username}!"
        if self.auth_manager.current_user.is_admin:
            welcome_text += " (Адміністратор)"

        title_label = ttk.Label(
            main_frame, text=welcome_text, style='Title.TLabel')
        title_label.pack(pady=(0, 30))

        # Меню опцій
        menu_frame = ttk.Frame(main_frame)
        menu_frame.pack(expand=True)

        # Кнопки меню
        ttk.Button(menu_frame, text="Почати тестування", command=self.show_category_selection,
                   style='Custom.TButton', width=25).pack(pady=10)

        ttk.Button(menu_frame, text="Переглянути результати", command=self.show_results,
                   style='Custom.TButton', width=25).pack(pady=10)

        ttk.Button(menu_frame, text="Статистика", command=self.show_statistics,
                   style='Custom.TButton', width=25).pack(pady=10)

        if self.auth_manager.current_user.is_admin:
            ttk.Button(menu_frame, text="Адміністрування", command=self.show_admin_panel,
                       style='Custom.TButton', width=25).pack(pady=10)

        ttk.Button(menu_frame, text="Налаштування", command=self.show_settings,
                   style='Custom.TButton', width=25).pack(pady=10)

        ttk.Button(menu_frame, text="Вихід", command=self.logout,
                   style='Custom.TButton', width=25).pack(pady=20)

    def show_category_selection(self):
        """Вибір категорії для тестування"""
        self.clear_window()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')

        title_label = ttk.Label(
            main_frame, text="Виберіть категорію для тестування", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Фрейм для категорій
        categories_frame = ttk.Frame(main_frame)
        categories_frame.pack(expand=True, fill='both')

        # Отримуємо категорії
        categories = self.test_manager.get_categories()

        for category in categories:
            category_frame = ttk.LabelFrame(
                categories_frame, text=category[1], padding="10")
            category_frame.pack(pady=5, padx=20, fill='x')

            ttk.Label(category_frame, text=category[2]).pack(anchor='w')

            button_frame = ttk.Frame(category_frame)
            button_frame.pack(fill='x', pady=5)

            ttk.Button(button_frame, text="Легкий тест (5 питань)",
                       command=lambda c=category[0]: self.start_test(c, 5)).pack(side='left', padx=(0, 10))
            ttk.Button(button_frame, text="Стандартний тест (10 питань)",
                       command=lambda c=category[0]: self.start_test(c, 10)).pack(side='left', padx=(0, 10))
            ttk.Button(button_frame, text="Розширений тест (15 питань)",
                       command=lambda c=category[0]: self.start_test(c, 15)).pack(side='left')

        # Кнопка назад
        ttk.Button(main_frame, text="Назад до меню",
                   command=self.show_main_menu).pack(pady=20)

    def start_test(self, category_id: int, num_questions: int):
        """Початок тестування"""
        if self.test_manager.start_test(category_id, num_questions):
            self.show_test_question()
        else:
            messagebox.showerror(
                "Помилка", "Недостатньо питань в цій категорії")

    def show_test_question(self):
        """Показ питання тесту"""
        question = self.test_manager.get_current_question()
        if not question:
            self.finish_test()
            return

        self.clear_window()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')

        # Прогрес
        progress_text = f"Питання {self.test_manager.current_question_index + 1} з {len(self.test_manager.current_questions)}"
        progress_label = ttk.Label(
            main_frame, text=progress_text, style='Heading.TLabel')
        progress_label.pack(pady=(0, 10))

        # Прогрес-бар
        progress_bar = ttk.Progressbar(
            main_frame, length=400, mode='determinate')
        progress_bar['value'] = ((self.test_manager.current_question_index) /
                                 len(self.test_manager.current_questions)) * 100
        progress_bar.pack(pady=(0, 20))

        # Питання
        question_frame = ttk.LabelFrame(
            main_frame, text=f"Складність: {'⭐' * question.difficulty}", padding="20")
        question_frame.pack(fill='both', expand=True, pady=10)

        question_label = ttk.Label(
            question_frame, text=question.question_text, wraplength=600, style='Heading.TLabel')
        question_label.pack(pady=(0, 20))

        # Варіанти відповідей
        self.answer_var = tk.StringVar()

        if question.question_type == "multiple_choice":
            for option in question.options:
                ttk.Radiobutton(question_frame, text=option, variable=self.answer_var,
                                value=option).pack(anchor='w', pady=2)

        elif question.question_type == "true_false":
            ttk.Radiobutton(question_frame, text="Правда", variable=self.answer_var,
                            value="True").pack(anchor='w', pady=2)
            ttk.Radiobutton(question_frame, text="Неправда", variable=self.answer_var,
                            value="False").pack(anchor='w', pady=2)

        elif question.question_type == "text_input":
            ttk.Label(question_frame, text="Введіть відповідь:").pack(
                anchor='w')
            self.answer_entry = ttk.Entry(question_frame, width=50)
            self.answer_entry.pack(pady=5, fill='x')
            self.answer_entry.focus()

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20, fill='x')

        ttk.Button(button_frame, text="Наступне питання",
                   command=self.submit_answer).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Завершити тест",
                   command=self.finish_test).pack(side='right')

        # Обробка Enter для текстового вводу
        if question.question_type == "text_input":
            self.root.bind('<Return>', lambda e: self.submit_answer())

    def submit_answer(self):
        """Подача відповіді"""
        question = self.test_manager.get_current_question()
        if not question:
            return

        if question.question_type == "text_input":
            answer = self.answer_entry.get().strip()
        else:
            answer = self.answer_var.get()

        if not answer:
            messagebox.showwarning(
                "Увага", "Будь ласка, оберіть або введіть відповідь")
            return

        self.test_manager.submit_answer(answer)
        self.show_test_question()

    def finish_test(self):
        """Завершення тесту"""
        if not self.test_manager.current_questions:
            self.show_main_menu()
            return

        results = self.test_manager.finish_test(
            self.auth_manager.current_user.user_id)
        self.show_test_results(results)

    def show_test_results(self, results: Dict):
        """Показ результатів тесту"""
        self.clear_window()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')

        title_label = ttk.Label(
            main_frame, text="Результати тестування", style='Title.TLabel')
        title_label.pack(pady=(0, 30))

        # Результати
        results_frame = ttk.LabelFrame(
            main_frame, text="Ваші результати", padding="20")
        results_frame.pack(fill='x', pady=10)

        ttk.Label(results_frame, text=f"Правильних відповідей: {results['correct_answers']} з {results['total_questions']}",
                  style='Heading.TLabel').pack(anchor='w', pady=5)

        ttk.Label(results_frame, text=f"Відсоток правильних відповідей: {results['percentage']}%",
                  style='Heading.TLabel').pack(anchor='w', pady=5)

        ttk.Label(results_frame, text=f"Час виконання: {results['time_spent']} секунд",
                  style='Heading.TLabel').pack(anchor='w', pady=5)

        # Оцінка
        percentage = results['percentage']
        if percentage >= 90:
            grade = "Відмінно! 🏆"
            grade_style = 'Success.TLabel'
        elif percentage >= 75:
            grade = "Добре! 👍"
            grade_style = 'Success.TLabel'
        elif percentage >= 60:
            grade = "Задовільно 📚"
            grade_style = 'Heading.TLabel'
        else:
            grade = "Потрібно покращити знання 📖"
            grade_style = 'Error.TLabel'

        ttk.Label(results_frame, text=f"Оцінка: {grade}", style=grade_style).pack(
            anchor='w', pady=10)

        # Детальний розбір
        if self.test_manager.current_questions:
            details_frame = ttk.LabelFrame(
                main_frame, text="Детальний розбір", padding="10")
            details_frame.pack(fill='both', expand=True, pady=10)

            # Скролюючий текст
            details_text = scrolledtext.ScrolledText(
                details_frame, height=10, wrap=tk.WORD)
            details_text.pack(fill='both', expand=True)

            for i, question in enumerate(self.test_manager.current_questions):
                user_answer = self.test_manager.user_answers[i] if i < len(
                    self.test_manager.user_answers) else "Не відповів"
                is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()

                details_text.insert(
                    tk.END, f"Питання {i+1}: {question.question_text}\n")
                details_text.insert(tk.END, f"Ваша відповідь: {user_answer}\n")
                details_text.insert(
                    tk.END, f"Правильна відповідь: {question.correct_answer}\n")
                details_text.insert(
                    tk.END, f"Результат: {'✅ Правильно' if is_correct else '❌ Неправильно'}\n")
                if question.explanation:
                    details_text.insert(
                        tk.END, f"Пояснення: {question.explanation}\n")
                details_text.insert(tk.END, "-" * 50 + "\n\n")

            details_text.config(state='disabled')

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20, fill='x')

        ttk.Button(button_frame, text="Пройти ще раз",
                   command=self.show_category_selection).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Головне меню",
                   command=self.show_main_menu).pack(side='left')

    def show_results(self):
        """Показ історії результатів"""
        self.clear_window()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')

        title_label = ttk.Label(
            main_frame, text="Історія результатів", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Отримуємо результати з бази
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT tr.test_date, c.name, tr.total_questions, tr.correct_answers, tr.time_spent
            FROM test_results tr
            JOIN categories c ON tr.category_id = c.id
            WHERE tr.user_id = ?
            ORDER BY tr.test_date DESC
            LIMIT 20
        ''', (self.auth_manager.current_user.user_id,))

        results = cursor.fetchall()
        conn.close()

        if not results:
            ttk.Label(main_frame, text="Ви ще не проходили тестування",
                      style='Heading.TLabel').pack(pady=50)
        else:
            # Таблиця результатів
            columns = ('Дата', 'Категорія', 'Питань',
                       'Правильно', 'Відсоток', 'Час')
            tree = ttk.Treeview(main_frame, columns=columns,
                                show='headings', height=15)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)

            for result in results:
                date = result[0][:16]
                category = result[1]
                total = result[2]
                correct = result[3]
                percentage = round((correct / total) * 100, 1)
                time_spent = f"{result[4]}с"

                tree.insert('', 'end', values=(date, category, total,
                            correct, f"{percentage}%", time_spent))

            tree.pack(fill='both', expand=True, pady=10)

            # Скролбар
            scrollbar = ttk.Scrollbar(
                main_frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side='right', fill='y')

        ttk.Button(main_frame, text="Назад",
                   command=self.show_main_menu).pack(pady=20)

    def show_statistics(self):
        """Показ статистики користувача"""
        self.clear_window()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')

        title_label = ttk.Label(
            main_frame, text="Статистика", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Отримуємо статистику
        conn = sqlite3.connect(self.db_manager.db_name)
        cursor = conn.cursor()

        # Загальна статистика
        cursor.execute('''
            SELECT COUNT(*), AVG(CAST(correct_answers AS FLOAT) / total_questions * 100), SUM(time_spent)
            FROM test_results
            WHERE user_id = ?
        ''', (self.auth_manager.current_user.user_id,))

        general_stats = cursor.fetchone()

        # Статистика по категоріях
        cursor.execute('''
            SELECT c.name, COUNT(*), AVG(CAST(tr.correct_answers AS FLOAT) / tr.total_questions * 100)
            FROM test_results tr
            JOIN categories c ON tr.category_id = c.id
            WHERE tr.user_id = ?
            GROUP BY c.name
        ''', (self.auth_manager.current_user.user_id,))

        category_stats = cursor.fetchall()
        conn.close()

        if general_stats[0] == 0:
            ttk.Label(main_frame, text="Статистика недоступна - пройдіть хоча б один тест",
                      style='Heading.TLabel').pack(pady=50)
        else:
            # Загальна статистика
            general_frame = ttk.LabelFrame(
                main_frame, text="Загальна статистика", padding="15")
            general_frame.pack(fill='x', pady=10)

            ttk.Label(general_frame, text=f"Всього тестів пройдено: {general_stats[0]}",
                      style='Heading.TLabel').pack(anchor='w', pady=2)
            ttk.Label(general_frame, text=f"Середній відсоток правильних відповідей: {general_stats[1]:.1f}%",
                      style='Heading.TLabel').pack(anchor='w', pady=2)
            ttk.Label(general_frame, text=f"Загальний час тестування: {general_stats[2]} секунд",
                      style='Heading.TLabel').pack(anchor='w', pady=2)

            # Статистика по категоріях
            if category_stats:
                category_frame = ttk.LabelFrame(
                    main_frame, text="Статистика по категоріях", padding="15")
                category_frame.pack(fill='both', expand=True, pady=10)

                for cat_stat in category_stats:
                    cat_text = f"{cat_stat[0]}: {cat_stat[1]} тестів, середній результат {cat_stat[2]:.1f}%"
                    ttk.Label(category_frame, text=cat_text).pack(
                        anchor='w', pady=2)

        ttk.Button(main_frame, text="Назад",
                   command=self.show_main_menu).pack(pady=20)

    def show_admin_panel(self):
        """Адміністративна панель"""
        if not self.auth_manager.current_user.is_admin:
            messagebox.showerror("Помилка", "Доступ заборонено")
            return

        self.clear_window()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')

        title_label = ttk.Label(
            main_frame, text="Адміністративна панель", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Кнопки адміністрування
        admin_frame = ttk.Frame(main_frame)
        admin_frame.pack(expand=True)

        ttk.Button(admin_frame, text="Управління питаннями", command=self.show_question_management,
                   style='Custom.TButton', width=25).pack(pady=10)

        ttk.Button(admin_frame, text="Управління користувачами", command=self.show_user_management,
                   style='Custom.TButton', width=25).pack(pady=10)

        ttk.Button(admin_frame, text="Статистика системи", command=self.show_system_statistics,
                   style='Custom.TButton', width=25).pack(pady=10)

        ttk.Button(admin_frame, text="Експорт даних", command=self.export_data,
                   style='Custom.TButton', width=25).pack(pady=10)

        ttk.Button(admin_frame, text="Назад", command=self.show_main_menu,
                   style='Custom.TButton', width=25).pack(pady=20)

    def show_question_management(self):
        """Управління питаннями"""
        messagebox.showinfo(
            "Інформація", "Функція управління питаннями буде реалізована в наступній версії")

    def show_user_management(self):
        """Управління користувачами"""
        messagebox.showinfo(
            "Інформація", "Функція управління користувачами буде реалізована в наступній версії")

    def show_system_statistics(self):
        """Системна статистика"""
        messagebox.showinfo(
            "Інформація", "Функція системної статистики буде реалізована в наступній версії")

    def export_data(self):
        """Експорт даних"""
        messagebox.showinfo(
            "Інформація", "Функція експорту даних буде реалізована в наступній версії")

    def show_settings(self):
        """Налаштування"""
        self.clear_window()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill='both')

        title_label = ttk.Label(
            main_frame, text="Налаштування", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        settings_frame = ttk.LabelFrame(
            main_frame, text="Налаштування профілю", padding="20")
        settings_frame.pack(fill='x', pady=10)

        # Інформація про користувача
        user = self.auth_manager.current_user
        ttk.Label(settings_frame, text=f"Ім'я користувача: {user.username}", style='Heading.TLabel').pack(
            anchor='w', pady=5)
        ttk.Label(settings_frame, text=f"Email: {user.email or 'Не вказано'}", style='Heading.TLabel').pack(
            anchor='w', pady=5)
        ttk.Label(settings_frame, text=f"Тип акаунту: {'Адміністратор' if user.is_admin else 'Користувач'}",
                  style='Heading.TLabel').pack(anchor='w', pady=5)

        # Кнопки налаштувань
        ttk.Button(settings_frame, text="Змінити пароль",
                   command=self.change_password).pack(pady=10)

        ttk.Button(main_frame, text="Назад",
                   command=self.show_main_menu).pack(pady=20)

    def change_password(self):
        """Зміна паролю"""
        messagebox.showinfo(
            "Інформація", "Функція зміни паролю буде реалізована в наступній версії")

    def logout(self):
        """Вихід з системи"""
        self.auth_manager.logout_user()
        self.show_login_screen()

    def run(self):
        """Запуск додатку"""
        self.root.mainloop()


if __name__ == "__main__":
    app = InformaticsTrainerGUI()
    app.run()
