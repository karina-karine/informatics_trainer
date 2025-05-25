"""
Розширений генератор демонстраційних даних для тренажера з інформатики
Версія 2.0 - з повним функціоналом та даними
"""

import sqlite3
import json
import random
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sys


class ProgressBar:
    """Простий прогрес-бар для консолі"""

    def __init__(self, total: int, prefix: str = "Прогрес", length: int = 50):
        self.total = total
        self.prefix = prefix
        self.length = length
        self.current = 0

    def update(self, step: int = 1):
        """Оновлення прогрес-бару"""
        self.current += step
        percent = (self.current / self.total) * 100
        filled_length = int(self.length * self.current // self.total)
        bar = '█' * filled_length + '-' * (self.length - filled_length)

        sys.stdout.write(
            f'\r{self.prefix} |{bar}| {percent:.1f}% ({self.current}/{self.total})')
        sys.stdout.flush()

        if self.current >= self.total:
            print()  # Новий рядок після завершення


class EnhancedDemoDataGenerator:
    """Розширений клас для генерації демонстраційних даних"""

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.stats = {
            'users_created': 0,
            'questions_created': 0,
            'test_results_created': 0,
            'answer_details_created': 0
        }

    def clear_demo_data(self):
        """Очищення існуючих демонстраційних даних"""
        print("Очищення існуючих демонстраційних даних...")

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            # Видаляємо в правильному порядку (через зовнішні ключі)
            cursor.execute("DELETE FROM answer_details")
            cursor.execute("DELETE FROM test_results")
            # Залишаємо базові питання
            cursor.execute("DELETE FROM questions WHERE id > 50")
            cursor.execute(
                "DELETE FROM users WHERE username LIKE 'demo_%' OR username LIKE '%.%'")

            conn.commit()
            print("✅ Демонстраційні дані очищено")

        except Exception as e:
            print(f"❌ Помилка очищення: {e}")
            conn.rollback()
        finally:
            conn.close()

    def generate_realistic_users(self, count: int = 25):
        """Генерація користувачів"""
        print(f"Генерація {count} користувачів...")

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Розширені списки українських імен
        male_names = [
            "Олександр", "Іван", "Петро", "Михайло", "Андрій", "Сергій",
            "Дмитро", "Володимир", "Роман", "Віталій", "Максим", "Артем",
            "Богдан", "Денис", "Євген", "Ігор", "Костянтин", "Леонід",
            "Микола", "Олег", "Павло", "Руслан", "Станіслав", "Тарас",
            "Юрій", "Ярослав", "Валентин", "Геннадій", "Едуард", "Захар"
        ]

        female_names = [
            "Марія", "Анна", "Катерина", "Ольга", "Наталія", "Юлія",
            "Тетяна", "Ірина", "Світлана", "Людмила", "Валентина", "Галина",
            "Оксана", "Лариса", "Вікторія", "Алла", "Віра", "Дарина",
            "Елена", "Жанна", "Зоя", "Інна", "Карина", "Лілія",
            "Маргарита", "Надія", "Поліна", "Регіна", "Софія", "Уляна"
        ]

        last_names = [
            "Іваненко", "Петренко", "Сидоренко", "Коваленко", "Бондаренко",
            "Ткаченко", "Кравченко", "Шевченко", "Поліщук", "Лисенко",
            "Мельник", "Гриценко", "Савченко", "Руденко", "Марченко",
            "Левченко", "Семенко", "Павленко", "Гончаренко", "Романенко",
            "Степаненко", "Панченко", "Литвиненко", "Назаренко", "Тимченко",
            "Федоренко", "Харченко", "Цимбаленко", "Чернenko", "Шульга"
        ]

        # Домени електронної пошти
        email_domains = [
            "gmail.com", "ukr.net", "i.ua", "outlook.com", "yahoo.com",
            "meta.ua", "bigmir.net", "rambler.ru", "mail.ru", "hotmail.com"
        ]

        # Професії/спеціальності для реалістичності
        professions = [
            "студент", "програміст", "вчитель", "інженер", "менеджер",
            "дизайнер", "аналітик", "тестувальник", "адміністратор", "консультант"
        ]

        progress = ProgressBar(count, "Створення користувачів")

        for i in range(count):
            # Випадковий вибір статі та імені
            is_male = random.choice([True, False])
            first_name = random.choice(male_names if is_male else female_names)
            last_name = random.choice(last_names)
            profession = random.choice(professions)

            # Генерація username
            username_variants = [
                f"{first_name.lower()}.{last_name.lower()}",
                f"{first_name.lower()}_{last_name.lower()}",
                f"{first_name.lower()}{random.randint(10, 99)}",
                f"{profession}_{first_name.lower()}",
                f"{first_name.lower()}.{profession}",
                f"user_{first_name.lower()}_{random.randint(100, 999)}"
            ]

            username = random.choice(username_variants)

            # Генерація email
            email_variants = [
                f"{username}@{random.choice(email_domains)}",
                f"{first_name.lower()}.{last_name.lower()}@{random.choice(email_domains)}",
                f"{first_name.lower()}{random.randint(1, 99)}@{random.choice(email_domains)}"
            ]

            email = random.choice(email_variants)

            # Генерація пароля
            password_base = random.choice([
                f"{first_name.lower()}{random.randint(100, 999)}",
                f"demo{random.randint(100, 999)}",
                f"{profession}{random.randint(10, 99)}",
                f"test{random.randint(1000, 9999)}"
            ])

            password_hash = hashlib.sha256(password_base.encode()).hexdigest()

            # Випадкова дата реєстрації (останні 8 місяців)
            days_ago = random.randint(1, 240)
            reg_date = datetime.now() - timedelta(days=days_ago)

            # 10% шанс бути адміністратором
            is_admin = random.random() < 0.1

            try:
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, registration_date, is_admin)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, password_hash, email, reg_date.isoformat(), is_admin))

                self.stats['users_created'] += 1

                # Зберігаємо пароль для звіту
                if i < 5:
                    print(
                        f"\n  {username} | пароль: {password_base} | {'👑 адмін' if is_admin else '👤 користувач'}")

            except sqlite3.IntegrityError:
                # Якщо користувач вже існує, генеруємо новий
                username = f"{username}_{random.randint(1, 999)}"
                try:
                    cursor.execute('''
                        INSERT INTO users (username, password_hash, email, registration_date, is_admin)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (username, password_hash, email, reg_date.isoformat(), is_admin))
                    self.stats['users_created'] += 1
                except:
                    pass

            progress.update()
            time.sleep(0.01)

        conn.commit()
        conn.close()
        print(f"✅ Створено {self.stats['users_created']} користувачів")

    def generate_comprehensive_questions(self):
        """Генерація повного набору питань для всіх категорій"""
        print("Генерація розширеного набору питань...")

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Отримуємо категорії
        cursor.execute("SELECT id, name FROM categories")
        categories = dict(cursor.fetchall())

        # Розширений набір питань для кожної категорії
        comprehensive_questions = {
            "Основи програмування": [
                # Легкі питання
                {
                    "question": "Що таке змінна в програмуванні?",
                    "type": "multiple_choice",
                    "answer": "Іменована область пам'яті для зберігання даних",
                    "options": [
                        "Іменована область пам'яті для зберігання даних",
                        "Функція для обчислень",
                        "Цикл для повторення коду",
                        "Умовний оператор"
                    ],
                    "difficulty": 1,
                    "explanation": "Змінна - це іменована область пам'яті, яка зберігає значення певного типу даних"
                },
                {
                    "question": "Яка різниця між компіляцією та інтерпретацією?",
                    "type": "text_input",
                    "answer": "Компіляція перетворює код в машинний код заздалегідь, інтерпретація виконує код рядок за рядком",
                    "options": None,
                    "difficulty": 2,
                    "explanation": "Компілятор перетворює весь код в машинний код перед виконанням, інтерпретатор виконує код по рядках"
                },
                {
                    "question": "Python є інтерпретованою мовою програмування",
                    "type": "true_false",
                    "answer": "True",
                    "options": None,
                    "difficulty": 1,
                    "explanation": "Python використовує інтерпретатор для виконання коду"
                },
                {
                    "question": "Що виведе код: print(2 ** 3)?",
                    "type": "multiple_choice",
                    "answer": "8",
                    "options": ["6", "8", "9", "23"],
                    "difficulty": 1,
                    "explanation": "Оператор ** означає піднесення до степеня, 2³ = 8"
                },
                {
                    "question": "Яка функція використовується для отримання довжини списку в Python?",
                    "type": "text_input",
                    "answer": "len",
                    "options": None,
                    "difficulty": 1,
                    "explanation": "Функція len() повертає кількість елементів в послідовності"
                },
                # Середні питання
                {
                    "question": "Що таке рекурсія в програмуванні?",
                    "type": "multiple_choice",
                    "answer": "Виклик функцією самої себе",
                    "options": [
                        "Виклик функцією самої себе",
                        "Повторення циклу",
                        "Створення нової змінної",
                        "Обробка помилок"
                    ],
                    "difficulty": 2,
                    "explanation": "Рекурсія - це техніка, коли функція викликає саму себе для розв'язання підзадач"
                },
                {
                    "question": "Яка складність алгоритму лінійного пошуку?",
                    "type": "multiple_choice",
                    "answer": "O(n)",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
                    "difficulty": 2,
                    "explanation": "Лінійний пошук перевіряє кожен елемент, тому має лінійну складність O(n)"
                },
                {
                    "question": "Декоратори в Python дозволяють модифікувати поведінку функцій",
                    "type": "true_false",
                    "answer": "True",
                    "options": None,
                    "difficulty": 3,
                    "explanation": "Декоратори - це функції, які приймають іншу функцію і розширюють її поведінку"
                },
                # Важкі питання
                {
                    "question": "Що таке замикання (closure) в програмуванні?",
                    "type": "text_input",
                    "answer": "Функція з доступом до змінних зовнішньої області видимості",
                    "options": None,
                    "difficulty": 3,
                    "explanation": "Замикання - це функція, яка має доступ до змінних з зовнішньої області видимості навіть після завершення виконання зовнішньої функції"
                }
            ],

            "Алгоритми та структури даних": [
                {
                    "question": "Яка структура даних використовує принцип LIFO?",
                    "type": "multiple_choice",
                    "answer": "Стек",
                    "options": ["Черга", "Стек", "Список", "Дерево"],
                    "difficulty": 1,
                    "explanation": "LIFO (Last In, First Out) - принцип роботи стеку"
                },
                {
                    "question": "Бінарне дерево пошуку завжди збалансоване",
                    "type": "true_false",
                    "answer": "False",
                    "options": None,
                    "difficulty": 2,
                    "explanation": "Звичайне бінарне дерево пошуку може бути незбалансованим, для збалансованості потрібні спеціальні алгоритми"
                },
                {
                    "question": "Яка середня складність операції пошуку в хеш-таблиці?",
                    "type": "multiple_choice",
                    "answer": "O(1)",
                    "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
                    "difficulty": 2,
                    "explanation": "Хеш-таблиця забезпечує константний час пошуку в середньому випадку"
                },
                {
                    "question": "Алгоритм Дейкстри знаходить найкоротший шлях в графі",
                    "type": "true_false",
                    "answer": "True",
                    "options": None,
                    "difficulty": 3,
                    "explanation": "Алгоритм Дейкстри знаходить найкоротші шляхи від одної вершини до всіх інших"
                },
                {
                    "question": "Що таке динамічне програмування?",
                    "type": "text_input",
                    "answer": "Метод розв'язання задач шляхом розбиття на підзадачі та збереження результатів",
                    "options": None,
                    "difficulty": 3,
                    "explanation": "Динамічне програмування - це техніка оптимізації, яка зберігає результати підзадач для уникнення повторних обчислень"
                }
            ],

            "Бази даних": [
                {
                    "question": "Що означає SQL?",
                    "type": "multiple_choice",
                    "answer": "Structured Query Language",
                    "options": [
                        "Structured Query Language",
                        "Simple Query Language",
                        "Standard Query Language",
                        "System Query Language"
                    ],
                    "difficulty": 1,
                    "explanation": "SQL - Structured Query Language, мова структурованих запитів"
                },
                {
                    "question": "Первинний ключ може містити NULL значення",
                    "type": "true_false",
                    "answer": "False",
                    "options": None,
                    "difficulty": 1,
                    "explanation": "Первинний ключ не може містити NULL значення і повинен бути унікальним"
                },
                {
                    "question": "Яка команда створює нову таблицю в SQL?",
                    "type": "text_input",
                    "answer": "CREATE TABLE",
                    "options": None,
                    "difficulty": 1,
                    "explanation": "Команда CREATE TABLE використовується для створення нових таблиць"
                },
                {
                    "question": "Що таке нормалізація бази даних?",
                    "type": "multiple_choice",
                    "answer": "Процес організації даних для зменшення надмірності",
                    "options": [
                        "Процес організації даних для зменшення надмірності",
                        "Створення резервних копій",
                        "Оптимізація запитів",
                        "Шифрування даних"
                    ],
                    "difficulty": 2,
                    "explanation": "Нормалізація зменшує дублювання даних та покращує цілісність бази даних"
                },
                {
                    "question": "ACID властивості забезпечують надійність транзакцій",
                    "type": "true_false",
                    "answer": "True",
                    "options": None,
                    "difficulty": 3,
                    "explanation": "ACID (Atomicity, Consistency, Isolation, Durability) - основні властивості надійних транзакцій"
                }
            ],

            "Мережі та Інтернет": [
                {
                    "question": "Що означає HTTP?",
                    "type": "multiple_choice",
                    "answer": "HyperText Transfer Protocol",
                    "options": [
                        "HyperText Transfer Protocol",
                        "HyperText Transport Protocol",
                        "High Transfer Text Protocol",
                        "HyperLink Transfer Protocol"
                    ],
                    "difficulty": 1,
                    "explanation": "HTTP - протокол передачі гіпертексту, основа веб-комунікацій"
                },
                {
                    "question": "IP-адреса версії 4 складається з 4 октетів",
                    "type": "true_false",
                    "answer": "True",
                    "options": None,
                    "difficulty": 1,
                    "explanation": "IPv4 адреса має формат xxx.xxx.xxx.xxx, де кожен xxx - це октет (0-255)"
                },
                {
                    "question": "Який порт за замовчуванням використовує HTTPS?",
                    "type": "text_input",
                    "answer": "443",
                    "options": None,
                    "difficulty": 2,
                    "explanation": "HTTPS використовує порт 443, а HTTP - порт 80"
                },
                {
                    "question": "Що таке DNS?",
                    "type": "multiple_choice",
                    "answer": "Domain Name System",
                    "options": [
                        "Domain Name System",
                        "Data Network Service",
                        "Dynamic Network System",
                        "Digital Name Service"
                    ],
                    "difficulty": 2,
                    "explanation": "DNS перетворює доменні імена в IP-адреси"
                },
                {
                    "question": "TCP гарантує доставку пакетів у правильному порядку",
                    "type": "true_false",
                    "answer": "True",
                    "options": None,
                    "difficulty": 2,
                    "explanation": "TCP - надійний протокол, який гарантує доставку та порядок пакетів"
                }
            ],

            "Операційні системи": [
                {
                    "question": "Що таке процес в операційній системі?",
                    "type": "multiple_choice",
                    "answer": "Програма, що виконується",
                    "options": [
                        "Програма, що виконується",
                        "Файл на диску",
                        "Область пам'яті",
                        "Мережеве з'єднання"
                    ],
                    "difficulty": 1,
                    "explanation": "Процес - це екземпляр програми, що виконується в пам'яті"
                },
                {
                    "question": "Віртуальна пам'ять дозволяє використовувати більше пам'яті, ніж фізично доступно",
                    "type": "true_false",
                    "answer": "True",
                    "options": None,
                    "difficulty": 2,
                    "explanation": "Віртуальна пам'ять використовує диск як розширення оперативної пам'яті"
                },
                {
                    "question": "Яка команда показує запущені процеси в Linux?",
                    "type": "text_input",
                    "answer": "ps",
                    "options": None,
                    "difficulty": 2,
                    "explanation": "Команда ps показує список активних процесів"
                },
                {
                    "question": "Що таке deadlock?",
                    "type": "multiple_choice",
                    "answer": "Взаємне блокування процесів",
                    "options": [
                        "Взаємне блокування процесів",
                        "Завершення процесу",
                        "Помилка пам'яті",
                        "Мережева помилка"
                    ],
                    "difficulty": 3,
                    "explanation": "Deadlock виникає, коли процеси взаємно блокують один одного, чекаючи ресурси"
                }
            ],

            "Інформаційна безпека": [
                {
                    "question": "Що таке хешування?",
                    "type": "multiple_choice",
                    "answer": "Перетворення даних у фіксований розмір",
                    "options": [
                        "Перетворення даних у фіксований розмір",
                        "Шифрування з ключем",
                        "Стиснення файлів",
                        "Резервне копіювання"
                    ],
                    "difficulty": 1,
                    "explanation": "Хешування створює унікальний відбиток даних фіксованого розміру"
                },
                {
                    "question": "Симетричне шифрування використовує один ключ для шифрування та розшифрування",
                    "type": "true_false",
                    "answer": "True",
                    "options": None,
                    "difficulty": 2,
                    "explanation": "При симетричному шифруванні той самий ключ використовується для обох операцій"
                },
                {
                    "question": "Що означає HTTPS?",
                    "type": "text_input",
                    "answer": "HTTP Secure",
                    "options": None,
                    "difficulty": 1,
                    "explanation": "HTTPS - це HTTP з шифруванням SSL/TLS"
                },
                {
                    "question": "Що таке фішинг?",
                    "type": "multiple_choice",
                    "answer": "Обман для отримання особистих даних",
                    "options": [
                        "Обман для отримання особистих даних",
                        "Вірусна атака",
                        "Блокування системи",
                        "Крадіжка обладнання"
                    ],
                    "difficulty": 2,
                    "explanation": "Фішинг - це соціальна інженерія для крадіжки особистих даних"
                },
                {
                    "question": "RSA є алгоритмом асиметричного шифрування",
                    "type": "true_false",
                    "answer": "True",
                    "options": None,
                    "difficulty": 3,
                    "explanation": "RSA використовує пару ключів: відкритий та закритий"
                }
            ]
        }

        total_questions = sum(len(questions)
                              for questions in comprehensive_questions.values())
        progress = ProgressBar(total_questions, "Додавання питань")

        # Додаємо питання до бази
        for category_name, questions in comprehensive_questions.items():
            # Знаходимо ID категорії
            category_id = None
            for cat_id, cat_name in categories.items():
                if category_name in cat_name or cat_name in category_name:
                    category_id = cat_id
                    break

            if category_id:
                for q in questions:
                    options_json = json.dumps(
                        q["options"], ensure_ascii=False) if q["options"] else None

                    try:
                        cursor.execute('''
                            INSERT INTO questions (category_id, question_text, question_type, 
                                                 correct_answer, options, difficulty, explanation)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (category_id, q["question"], q["type"], q["answer"],
                              options_json, q["difficulty"], q["explanation"]))

                        self.stats['questions_created'] += 1

                    except sqlite3.IntegrityError:
                        pass

                    progress.update()
                    time.sleep(0.005)

        conn.commit()
        conn.close()
        print(f"✅ Додано {self.stats['questions_created']} нових питань")

    def generate_realistic_test_results(self, num_results: int = 150):
        """Генерація реалістичних результатів тестування"""
        print(f"Генерація {num_results} результатів тестування...")

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Отримуємо користувачів та категорії
        cursor.execute("SELECT id FROM users WHERE is_admin = 0")
        user_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM categories")
        category_ids = [row[0] for row in cursor.fetchall()]

        if not user_ids or not category_ids:
            print("❌ Недостатньо користувачів або категорій")
            return

        progress = ProgressBar(num_results, "Генерація результатів")

        # Створюємо профілі користувачів (деякі кращі, деякі гірші)
        user_profiles = {}
        for user_id in user_ids:
            # Випадковий рівень навичок користувача
            skill_level = random.choice([
                'beginner',    # 30% - початківці
                'beginner',
                'beginner',
                'intermediate',  # 50% - середній рівень
                'intermediate',
                'intermediate',
                'intermediate',
                'intermediate',
                'advanced',    # 20% - просунуті
                'advanced'
            ])

            user_profiles[user_id] = {
                'skill_level': skill_level,
                'preferred_categories': random.sample(category_ids, random.randint(2, 4)),
                'activity_level': random.choice(['low', 'medium', 'high'])
            }

        for i in range(num_results):
            user_id = random.choice(user_ids)
            profile = user_profiles[user_id]

            # Вибираємо категорію (більша ймовірність для улюблених)
            if random.random() < 0.7 and profile['preferred_categories']:
                category_id = random.choice(profile['preferred_categories'])
            else:
                category_id = random.choice(category_ids)

            # Параметри тесту залежно від рівня активності
            if profile['activity_level'] == 'high':
                total_questions = random.choice([10, 15, 20])
            elif profile['activity_level'] == 'medium':
                total_questions = random.choice([5, 10, 15])
            else:
                total_questions = random.choice([5, 10])

            # Результати залежно від рівня навичок
            if profile['skill_level'] == 'advanced':
                # Просунуті користувачі: 70-95% правильних відповідей
                success_rate = random.uniform(0.7, 0.95)
            elif profile['skill_level'] == 'intermediate':
                # Середній рівень: 50-80% правильних відповідей
                success_rate = random.uniform(0.5, 0.8)
            else:
                # Початківці: 20-60% правильних відповідей
                success_rate = random.uniform(0.2, 0.6)

            correct_answers = max(
                0, min(total_questions, int(total_questions * success_rate)))

            # Час виконання залежно від навичок та кількості питань
            base_time_per_question = {
                'advanced': random.randint(30, 60),
                'intermediate': random.randint(45, 90),
                'beginner': random.randint(60, 120)
            }[profile['skill_level']]

            time_spent = total_questions * \
                base_time_per_question + random.randint(-30, 60)
            time_spent = max(30, time_spent)  # Мінімум 30 секунд

            # Випадкова дата тесту (останні 4 місяці, з більшою активністю останнім часом)
            if random.random() < 0.6:  # 60% тестів за останній місяць
                days_ago = random.randint(1, 30)
            else:  # 40% тестів за попередні 3 місяці
                days_ago = random.randint(31, 120)

            test_date = datetime.now() - timedelta(days=days_ago)

            # Додаємо випадковий час дня
            test_date = test_date.replace(
                hour=random.randint(8, 22),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )

            try:
                cursor.execute('''
                    INSERT INTO test_results (user_id, category_id, total_questions, 
                                            correct_answers, test_date, time_spent)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, category_id, total_questions, correct_answers,
                      test_date.isoformat(), time_spent))

                self.stats['test_results_created'] += 1

            except Exception as e:
                print(f"\n❌ Помилка створення результату: {e}")

            progress.update()
            time.sleep(0.01)

        conn.commit()
        conn.close()
        print(
            f"✅ Створено {self.stats['test_results_created']} результатів тестування")

    def generate_answer_details(self):
        """Генерація детальних відповідей для результатів тестування"""
        print("Генерація детальних відповідей...")

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Отримуємо всі результати тестування без детальних відповідей
        cursor.execute('''
            SELECT tr.id, tr.category_id, tr.total_questions, tr.correct_answers
            FROM test_results tr
            LEFT JOIN answer_details ad ON tr.id = ad.test_result_id
            WHERE ad.id IS NULL
        ''')

        test_results = cursor.fetchall()

        if not test_results:
            print("✅ Всі результати вже мають детальні відповіді")
            return

        progress = ProgressBar(len(test_results), "Генерація деталей")

        for test_result_id, category_id, total_questions, correct_answers in test_results:
            # Отримуємо питання для цієї категорії
            cursor.execute('''
                SELECT id, difficulty FROM questions 
                WHERE category_id = ? 
                ORDER BY RANDOM() 
                LIMIT ?
            ''', (category_id, total_questions))

            questions = cursor.fetchall()

            if len(questions) < total_questions:
                # Якщо питань недостатньо, беремо з інших категорій
                cursor.execute('''
                    SELECT id, difficulty FROM questions 
                    ORDER BY RANDOM() 
                    LIMIT ?
                ''', (total_questions - len(questions),))

                additional_questions = cursor.fetchall()
                questions.extend(additional_questions)

            # Визначаємо які відповіді будуть правильними
            correct_indices = random.sample(
                range(total_questions), correct_answers)

            for i, (question_id, difficulty) in enumerate(questions[:total_questions]):
                is_correct = i in correct_indices

                # Час відповіді залежить від складності та правильності
                if difficulty == 1:  # Легкі
                    base_time = random.randint(15, 45)
                elif difficulty == 2:  # Середні
                    base_time = random.randint(30, 90)
                else:  # Важкі
                    base_time = random.randint(45, 150)

                # Неправильні відповіді зазвичай швидші (здогадки) або повільніші (роздуми)
                if not is_correct:
                    if random.random() < 0.3:  # 30% швидких неправильних відповідей
                        base_time = int(base_time * 0.5)
                    elif random.random() < 0.3:  # 30% повільних неправильних відповідей
                        base_time = int(base_time * 1.5)

                answer_time = max(5, base_time + random.randint(-10, 20))

                cursor.execute('''
                    INSERT INTO answer_details (test_result_id, question_id, is_correct, answer_time)
                    VALUES (?, ?, ?, ?)
                ''', (test_result_id, question_id, is_correct, answer_time))

                self.stats['answer_details_created'] += 1

            progress.update()
            time.sleep(0.005)

        conn.commit()
        conn.close()
        print(
            f"✅ Створено {self.stats['answer_details_created']} детальних відповідей")

    def add_sample_categories(self):
        """Додавання додаткових категорій якщо їх мало"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]

        if category_count < 6:
            additional_categories = [
                ("Веб-розробка", "HTML, CSS, JavaScript, фреймворки"),
                ("Мобільна розробка", "Android, iOS, React Native, Flutter"),
                ("Машинне навчання", "Алгоритми ML, нейронні мережі, аналіз даних"),
                ("DevOps", "CI/CD, контейнеризація, хмарні технології"),
                ("Тестування ПЗ", "Методи тестування, автоматизація, QA")
            ]

            for name, description in additional_categories:
                try:
                    cursor.execute('''
                        INSERT INTO categories (name, description)
                        VALUES (?, ?)
                    ''', (name, description))
                    print(f"Додано категорію: {name}")
                except sqlite3.IntegrityError:
                    pass  # Категорія вже існує

            conn.commit()

        conn.close()

    def generate_all_demo_data(self, clear_existing: bool = False):
        """Генерація всіх демонстраційних даних"""
        print("ГЕНЕРАТОР ДЕМОНСТРАЦІЙНИХ ДАНИХ v2.0")
        print("=" * 60)
        print("Створення реалістичних даних для тестування адміністративної панелі")
        print("=" * 60)

        start_time = time.time()

        if clear_existing:
            self.clear_demo_data()

        print("\nЕтап 1: Підготовка структури")
        self.add_sample_categories()

        print("\nЕтап 2: Створення користувачів")
        self.generate_realistic_users(25)

        print("\nЕтап 3: Додавання питань")
        self.generate_comprehensive_questions()

        print("\nЕтап 4: Генерація результатів тестування")
        self.generate_realistic_test_results(120)

        print("\nЕтап 5: Створення детальних відповідей")
        self.generate_answer_details()

        end_time = time.time()
        duration = end_time - start_time

        print("\n" + "=" * 60)
        print("✅ ГЕНЕРАЦІЯ ЗАВЕРШЕНА УСПІШНО!")
        print("=" * 60)
        print(f"Час виконання: {duration:.2f} секунд")
        print(f"Користувачів створено: {self.stats['users_created']}")
        print(f"Питань додано: {self.stats['questions_created']}")
        print(f"Результатів тестів: {self.stats['test_results_created']}")
        print(
            f"Детальних відповідей: {self.stats['answer_details_created']}")
        print("\nТепер ви можете протестувати всі функції адміністративної панелі!")
        print("Для входу використовуйте створених користувачів або створіть нового адміністратора")

        # Показуємо кілька прикладів користувачів
        self.show_sample_users()

    def show_sample_users(self):
        """Показ прикладів створених користувачів"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        print("\nПРИКЛАДИ СТВОРЕНИХ КОРИСТУВАЧІВ:")
        print("-" * 50)

        # Показуємо адміністраторів
        cursor.execute('''
            SELECT username, is_admin FROM users 
            WHERE is_admin = 1 AND username LIKE '%.%'
            LIMIT 3
        ''')

        admins = cursor.fetchall()
        if admins:
            print("Адміністратори:")
            for username, _ in admins:
                print(f"   • {username} (пароль: demo123 або подібний)")

        # Показуємо звичайних користувачів
        cursor.execute('''
            SELECT username, is_admin FROM users 
            WHERE is_admin = 0 AND username LIKE '%.%'
            LIMIT 5
        ''')

        users = cursor.fetchall()
        if users:
            print("\nЗвичайні користувачі:")
            for username, _ in users:
                print(f"   • {username}")

        conn.close()
        print("\nПаролі зазвичай мають формат: demo123, test456, ім'я123 тощо")

    def create_admin_user(self, username: str = "admin", password: str = "admin123"):
        """Створення гарантованого адміністратора"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, registration_date, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, f"{username}@admin.local",
                  datetime.now().isoformat(), True))

            conn.commit()
            print(
                f"✅ Створено адміністратора: {username} | пароль: {password}")

        except sqlite3.IntegrityError:
            print(f"⚠️  Користувач {username} вже існує")

        conn.close()


def main():
    """Головна функція для запуску генератора"""
    print("РОЗШИРЕНИЙ ГЕНЕРАТОР ДЕМОНСТРАЦІЙНИХ ДАНИХ")
    print("Версія 2.0 - Повний функціонал для тестування")
    print("=" * 60)

    generator = EnhancedDemoDataGenerator("informatics_trainer.db")

    print("\nОберіть дію:")
    print("1. Повна генерація (очистити існуючі дані)")
    print("2. Додати дані (зберегти існуючі)")
    print("3. Створити тільки адміністратора")
    print("4. Очистити демо-дані")
    print("5. Вихід")

    while True:
        choice = input("\nВаш вибір (1-5): ").strip()

        if choice == "1":
            confirm = input(
                "⚠️  Це видалить всі існуючі демо-дані. Продовжити? (y/n): ").lower()
            if confirm in ['y', 'yes', 'так']:
                generator.generate_all_demo_data(clear_existing=True)
            break

        elif choice == "2":
            generator.generate_all_demo_data(clear_existing=False)
            break

        elif choice == "3":
            username = input(
                "Ім'я адміністратора (admin): ").strip() or "admin"
            password = input("Пароль (admin123): ").strip() or "admin123"
            generator.create_admin_user(username, password)
            break

        elif choice == "4":
            confirm = input(
                "⚠️  Це видалить всі демо-дані. Продовжити? (y/n): ").lower()
            if confirm in ['y', 'yes', 'так']:
                generator.clear_demo_data()
            break

        elif choice == "5":
            print("👋 До побачення!")
            break

        else:
            print("❌ Невірний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main()
