"""
Адміністративна панель для програми-тренажера з інформатики
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sqlite3
import json
import csv
import datetime
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


class QuestionManager:
    """Клас для управління питаннями"""

    def __init__(self, db_name: str):
        self.db_name = db_name

    def get_all_questions(self) -> List[Tuple]:
        """Отримання всіх питань"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT q.id, c.name, q.question_text, q.question_type, 
                   q.correct_answer, q.difficulty, q.usage_count
            FROM questions q
            JOIN categories c ON q.category_id = c.id
            ORDER BY c.name, q.difficulty, q.id
        ''')

        questions = cursor.fetchall()
        conn.close()
        return questions

    def get_categories(self) -> List[Tuple]:
        """Отримання всіх категорій"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name, description FROM categories ORDER BY name")
        categories = cursor.fetchall()

        conn.close()
        return categories

    def add_question(self, category_id: int, question_text: str, question_type: str,
                     correct_answer: str, options: List[str], difficulty: int,
                     explanation: str) -> bool:
        """Додавання нового питання"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            options_json = json.dumps(options) if options else None

            cursor.execute('''
                INSERT INTO questions (category_id, question_text, question_type, 
                                     correct_answer, options, difficulty, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (category_id, question_text, question_type, correct_answer,
                  options_json, difficulty, explanation))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Помилка додавання питання: {e}")
            return False

    def update_question(self, question_id: int, category_id: int, question_text: str,
                        question_type: str, correct_answer: str, options: List[str],
                        difficulty: int, explanation: str) -> bool:
        """Оновлення питання"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            options_json = json.dumps(options) if options else None

            cursor.execute('''
                UPDATE questions 
                SET category_id=?, question_text=?, question_type=?, 
                    correct_answer=?, options=?, difficulty=?, explanation=?
                WHERE id=?
            ''', (category_id, question_text, question_type, correct_answer,
                  options_json, difficulty, explanation, question_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Помилка оновлення питання: {e}")
            return False

    def delete_question(self, question_id: int) -> bool:
        """Видалення питання"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Перевіряємо чи використовується питання в результатах
            cursor.execute(
                "SELECT COUNT(*) FROM answer_details WHERE question_id = ?", (question_id,))
            usage_count = cursor.fetchone()[0]

            if usage_count > 0:
                # Не видаляємо, а позначаємо як неактивне
                cursor.execute(
                    "UPDATE questions SET is_active = 0 WHERE id = ?", (question_id,))
            else:
                # Видаляємо повністю
                cursor.execute(
                    "DELETE FROM questions WHERE id = ?", (question_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Помилка видалення питання: {e}")
            return False

    def add_category(self, name: str, description: str) -> bool:
        """Додавання нової категорії"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
                           (name, description))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Помилка додавання категорії: {e}")
            return False


class UserManager:
    """Клас для управління користувачами"""

    def __init__(self, db_name: str):
        self.db_name = db_name

    def get_all_users(self) -> List[Tuple]:
        """Отримання всіх користувачів"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.id, u.username, u.email, u.registration_date, u.is_admin,
                   COUNT(tr.id) as tests_count,
                   AVG(CAST(tr.correct_answers AS FLOAT) / tr.total_questions * 100) as avg_score
            FROM users u
            LEFT JOIN test_results tr ON u.id = tr.user_id
            GROUP BY u.id, u.username, u.email, u.registration_date, u.is_admin
            ORDER BY u.registration_date DESC
        ''')

        users = cursor.fetchall()
        conn.close()
        return users

    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Отримання детальної статистики користувача"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Загальна статистика
        cursor.execute('''
            SELECT COUNT(*) as total_tests,
                   SUM(total_questions) as total_questions,
                   SUM(correct_answers) as total_correct,
                   SUM(time_spent) as total_time,
                   AVG(CAST(correct_answers AS FLOAT) / total_questions * 100) as avg_percentage
            FROM test_results
            WHERE user_id = ?
        ''', (user_id,))

        general_stats = cursor.fetchone()

        # Статистика по категоріях
        cursor.execute('''
            SELECT c.name, COUNT(*) as tests_count,
                   AVG(CAST(tr.correct_answers AS FLOAT) / tr.total_questions * 100) as avg_score
            FROM test_results tr
            JOIN categories c ON tr.category_id = c.id
            WHERE tr.user_id = ?
            GROUP BY c.name
            ORDER BY avg_score DESC
        ''', (user_id,))

        category_stats = cursor.fetchall()

        # Останні тести
        cursor.execute('''
            SELECT c.name, tr.test_date, tr.total_questions, tr.correct_answers,
                   CAST(tr.correct_answers AS FLOAT) / tr.total_questions * 100 as percentage
            FROM test_results tr
            JOIN categories c ON tr.category_id = c.id
            WHERE tr.user_id = ?
            ORDER BY tr.test_date DESC
            LIMIT 10
        ''', (user_id,))

        recent_tests = cursor.fetchall()

        conn.close()

        return {
            'general': general_stats,
            'categories': category_stats,
            'recent_tests': recent_tests
        }

    def toggle_admin_status(self, user_id: int) -> bool:
        """Зміна статусу адміністратора"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET is_admin = NOT is_admin WHERE id = ?", (user_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Помилка зміни статусу: {e}")
            return False

    def delete_user(self, user_id: int) -> bool:
        """Видалення користувача"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Видаляємо пов'язані дані
            cursor.execute(
                "DELETE FROM answer_details WHERE test_result_id IN (SELECT id FROM test_results WHERE user_id = ?)", (user_id,))
            cursor.execute(
                "DELETE FROM test_results WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Помилка видалення користувача: {e}")
            return False


class SystemStatistics:
    """Клас для системної статистики"""

    def __init__(self, db_name: str):
        self.db_name = db_name

    def get_general_statistics(self) -> Dict[str, Any]:
        """Отримання загальної статистики системи"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Загальні показники
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        admin_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM questions")
        total_questions = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM categories")
        total_categories = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM test_results")
        total_tests = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(total_questions) FROM test_results")
        total_answered = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(correct_answers) FROM test_results")
        total_correct = cursor.fetchone()[0] or 0

        cursor.execute(
            "SELECT AVG(CAST(correct_answers AS FLOAT) / total_questions * 100) FROM test_results")
        avg_success_rate = cursor.fetchone()[0] or 0

        # Активність по днях (останні 30 днів)
        cursor.execute('''
            SELECT DATE(test_date) as test_day, COUNT(*) as tests_count
            FROM test_results
            WHERE test_date >= date('now', '-30 days')
            GROUP BY DATE(test_date)
            ORDER BY test_day
        ''')
        daily_activity = cursor.fetchall()

        # Популярність категорій
        cursor.execute('''
            SELECT c.name, COUNT(*) as tests_count
            FROM test_results tr
            JOIN categories c ON tr.category_id = c.id
            GROUP BY c.name
            ORDER BY tests_count DESC
        ''')
        category_popularity = cursor.fetchall()

        # Розподіл по складності
        cursor.execute('''
            SELECT q.difficulty, COUNT(ad.id) as answers_count
            FROM answer_details ad
            JOIN questions q ON ad.question_id = q.id
            GROUP BY q.difficulty
            ORDER BY q.difficulty
        ''')
        difficulty_distribution = cursor.fetchall()

        conn.close()

        return {
            'general': {
                'total_users': total_users,
                'admin_users': admin_users,
                'regular_users': total_users - admin_users,
                'total_questions': total_questions,
                'total_categories': total_categories,
                'total_tests': total_tests,
                'total_answered': total_answered,
                'total_correct': total_correct,
                'avg_success_rate': round(avg_success_rate, 2) if avg_success_rate else 0
            },
            'daily_activity': daily_activity,
            'category_popularity': category_popularity,
            'difficulty_distribution': difficulty_distribution
        }


class DataExporter:
    """Клас для експорту даних"""

    def __init__(self, db_name: str):
        self.db_name = db_name

    def export_to_csv(self, data_type: str, filename: str) -> bool:
        """Експорт даних у CSV формат"""
        try:
            conn = sqlite3.connect(self.db_name)

            if data_type == "users":
                df = pd.read_sql_query('''
                    SELECT u.id, u.username, u.email, u.registration_date, u.is_admin,
                           COUNT(tr.id) as tests_count,
                           AVG(CAST(tr.correct_answers AS FLOAT) / tr.total_questions * 100) as avg_score
                    FROM users u
                    LEFT JOIN test_results tr ON u.id = tr.user_id
                    GROUP BY u.id
                ''', conn)

            elif data_type == "questions":
                df = pd.read_sql_query('''
                    SELECT q.id, c.name as category, q.question_text, q.question_type,
                           q.correct_answer, q.difficulty, q.explanation
                    FROM questions q
                    JOIN categories c ON q.category_id = c.id
                ''', conn)

            elif data_type == "results":
                df = pd.read_sql_query('''
                    SELECT u.username, c.name as category, tr.test_date,
                           tr.total_questions, tr.correct_answers,
                           CAST(tr.correct_answers AS FLOAT) / tr.total_questions * 100 as percentage,
                           tr.time_spent
                    FROM test_results tr
                    JOIN users u ON tr.user_id = u.id
                    JOIN categories c ON tr.category_id = c.id
                    ORDER BY tr.test_date DESC
                ''', conn)

            else:
                return False

            df.to_csv(filename, index=False, encoding='utf-8')
            conn.close()
            return True

        except Exception as e:
            print(f"Помилка експорту CSV: {e}")
            return False

    def export_to_json(self, data_type: str, filename: str) -> bool:
        """Експорт даних у JSON формат"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            if data_type == "full_backup":
                # Повний бекап всіх даних
                data = {}

                # Користувачі
                cursor.execute("SELECT * FROM users")
                data['users'] = [dict(zip([col[0] for col in cursor.description], row))
                                 for row in cursor.fetchall()]

                # Категорії
                cursor.execute("SELECT * FROM categories")
                data['categories'] = [dict(zip([col[0] for col in cursor.description], row))
                                      for row in cursor.fetchall()]

                # Питання
                cursor.execute("SELECT * FROM questions")
                data['questions'] = [dict(zip([col[0] for col in cursor.description], row))
                                     for row in cursor.fetchall()]

                # Результати
                cursor.execute("SELECT * FROM test_results")
                data['test_results'] = [dict(zip([col[0] for col in cursor.description], row))
                                        for row in cursor.fetchall()]

                # Детальні відповіді
                cursor.execute("SELECT * FROM answer_details")
                data['answer_details'] = [dict(zip([col[0] for col in cursor.description], row))
                                          for row in cursor.fetchall()]

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            conn.close()
            return True

        except Exception as e:
            print(f"Помилка експорту JSON: {e}")
            return False

    def export_to_pdf(self, report_type: str, filename: str) -> bool:
        """Експорт звіту у PDF формат"""
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Заголовок
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1
            )

            if report_type == "system_report":
                story.append(
                    Paragraph("Звіт про стан системи тренажера", title_style))
                story.append(Spacer(1, 20))

                # Отримуємо статистику
                stats = SystemStatistics(self.db_name).get_general_statistics()

                # Загальна інформація
                general_data = [
                    ['Показник', 'Значення'],
                    ['Загальна кількість користувачів',
                        stats['general']['total_users']],
                    ['Адміністраторів', stats['general']['admin_users']],
                    ['Звичайних користувачів', stats['general']['regular_users']],
                    ['Загальна кількість питань',
                        stats['general']['total_questions']],
                    ['Кількість категорій', stats['general']['total_categories']],
                    ['Проведено тестів', stats['general']['total_tests']],
                    ['Середній відсоток успішності',
                        f"{stats['general']['avg_success_rate']}%"]
                ]

                table = Table(general_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                story.append(table)
                story.append(Spacer(1, 20))

                # Популярність категорій
                story.append(
                    Paragraph("Популярність категорій", styles['Heading2']))
                story.append(Spacer(1, 10))

                category_data = [['Категорія', 'Кількість тестів']]
                for cat_name, tests_count in stats['category_popularity']:
                    category_data.append([cat_name, tests_count])

                cat_table = Table(category_data)
                cat_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                story.append(cat_table)

            doc.build(story)
            return True

        except Exception as e:
            print(f"Помилка експорту PDF: {e}")
            return False


class AdminPanelGUI:
    """Графічний інтерфейс адміністративної панелі"""

    def __init__(self, parent, db_name: str, current_user):
        self.parent = parent
        self.db_name = db_name
        self.current_user = current_user

        # Ініціалізуємо менеджери
        self.question_manager = QuestionManager(db_name)
        self.user_manager = UserManager(db_name)
        self.statistics = SystemStatistics(db_name)
        self.exporter = DataExporter(db_name)

        # Створюємо головне вікно
        self.window = tk.Toplevel(parent)
        self.window.title("Адміністративна панель")
        self.window.geometry("1200x800")
        self.window.configure(bg='#f0f0f0')

        self.setup_main_interface()

    def setup_main_interface(self):
        """Налаштування головного інтерфейсу"""
        # Заголовок
        title_frame = ttk.Frame(self.window)
        title_frame.pack(fill='x', padx=20, pady=10)

        ttk.Label(title_frame, text="Адміністративна панель",
                  font=('Arial', 16, 'bold')).pack()

        # Головне меню
        menu_frame = ttk.Frame(self.window)
        menu_frame.pack(fill='x', padx=20, pady=10)

        # Кнопки меню
        ttk.Button(menu_frame, text="Управління питаннями",
                   command=self.show_question_management, width=25).pack(side='left', padx=5)
        ttk.Button(menu_frame, text="Управління користувачами",
                   command=self.show_user_management, width=25).pack(side='left', padx=5)
        ttk.Button(menu_frame, text="Статистика системи",
                   command=self.show_system_statistics, width=25).pack(side='left', padx=5)
        ttk.Button(menu_frame, text="Експорт даних",
                   command=self.show_export_options, width=25).pack(side='left', padx=5)

        # Робоча область
        self.work_frame = ttk.Frame(self.window)
        self.work_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Показуємо початкову інформацію
        self.show_dashboard()

    def clear_work_frame(self):
        """Очищення робочої області"""
        for widget in self.work_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Показ головної панелі"""
        self.clear_work_frame()

        # Швидка статистика
        stats = self.statistics.get_general_statistics()

        dashboard_frame = ttk.LabelFrame(
            self.work_frame, text="Огляд системи", padding="20")
        dashboard_frame.pack(fill='both', expand=True)

        # Статистичні картки
        cards_frame = ttk.Frame(dashboard_frame)
        cards_frame.pack(fill='x', pady=10)

        # Картка користувачів
        user_card = ttk.LabelFrame(
            cards_frame, text="Користувачі", padding="10")
        user_card.pack(side='left', fill='both', expand=True, padx=5)

        ttk.Label(user_card, text=str(stats['general']['total_users']),
                  font=('Arial', 24, 'bold')).pack()
        ttk.Label(user_card, text="Всього користувачів").pack()

        # Картка питань
        question_card = ttk.LabelFrame(
            cards_frame, text="Питання", padding="10")
        question_card.pack(side='left', fill='both', expand=True, padx=5)

        ttk.Label(question_card, text=str(stats['general']['total_questions']),
                  font=('Arial', 24, 'bold')).pack()
        ttk.Label(question_card, text="Всього питань").pack()

        # Картка тестів
        test_card = ttk.LabelFrame(cards_frame, text="Тести", padding="10")
        test_card.pack(side='left', fill='both', expand=True, padx=5)

        ttk.Label(test_card, text=str(stats['general']['total_tests']),
                  font=('Arial', 24, 'bold')).pack()
        ttk.Label(test_card, text="Проведено тестів").pack()

        # Картка успішності
        success_card = ttk.LabelFrame(
            cards_frame, text="Успішність", padding="10")
        success_card.pack(side='left', fill='both', expand=True, padx=5)

        ttk.Label(success_card, text=f"{stats['general']['avg_success_rate']}%",
                  font=('Arial', 24, 'bold')).pack()
        ttk.Label(success_card, text="Середня успішність").pack()

        # Графік активності
        if stats['daily_activity']:
            self.create_activity_chart(
                dashboard_frame, stats['daily_activity'])

    def create_activity_chart(self, parent, activity_data):
        """Створення графіку активності"""
        chart_frame = ttk.LabelFrame(
            parent, text="Активність за останні 30 днів", padding="10")
        chart_frame.pack(fill='both', expand=True, pady=10)

        fig, ax = plt.subplots(figsize=(10, 4))

        dates = [item[0] for item in activity_data]
        counts = [item[1] for item in activity_data]

        ax.plot(dates, counts, marker='o', linewidth=2, markersize=4)
        ax.set_title('Кількість тестів по днях')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Кількість тестів')
        ax.grid(True, alpha=0.3)

        # Поворот підписів дат
        plt.xticks(rotation=45)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_question_management(self):
        """Управління питаннями"""
        self.clear_work_frame()

        # Заголовок
        ttk.Label(self.work_frame, text="Управління питаннями",
                  font=('Arial', 14, 'bold')).pack(pady=10)

        # Панель кнопок
        button_frame = ttk.Frame(self.work_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(button_frame, text="Додати питання",
                   command=self.add_question_dialog).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Редагувати",
                   command=self.edit_question_dialog).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Видалити",
                   command=self.delete_question).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Оновити",
                   command=self.refresh_questions).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Додати категорію",
                   command=self.add_category_dialog).pack(side='right', padx=5)

        # Таблиця питань
        table_frame = ttk.Frame(self.work_frame)
        table_frame.pack(fill='both', expand=True, pady=10)

        columns = ('ID', 'Категорія', 'Питання',
                   'Тип', 'Складність', 'Використання')
        self.questions_tree = ttk.Treeview(
            table_frame, columns=columns, show='headings', height=20)

        # Налаштування колонок
        self.questions_tree.heading('ID', text='ID')
        self.questions_tree.heading('Категорія', text='Категорія')
        self.questions_tree.heading('Питання', text='Питання')
        self.questions_tree.heading('Тип', text='Тип')
        self.questions_tree.heading('Складність', text='Складність')
        self.questions_tree.heading('Використання', text='Використання')

        self.questions_tree.column('ID', width=50)
        self.questions_tree.column('Категорія', width=150)
        self.questions_tree.column('Питання', width=400)
        self.questions_tree.column('Тип', width=120)
        self.questions_tree.column('Складність', width=100)
        self.questions_tree.column('Використання', width=100)

        # Скролбар
        scrollbar_q = ttk.Scrollbar(
            table_frame, orient='vertical', command=self.questions_tree.yview)
        self.questions_tree.configure(yscrollcommand=scrollbar_q.set)

        self.questions_tree.pack(side='left', fill='both', expand=True)
        scrollbar_q.pack(side='right', fill='y')

        # Завантажуємо дані
        self.refresh_questions()

    def refresh_questions(self):
        """Оновлення списку питань"""
        # Очищуємо таблицю
        for item in self.questions_tree.get_children():
            self.questions_tree.delete(item)

        # Завантажуємо питання
        questions = self.question_manager.get_all_questions()

        for question in questions:
            # Обрізаємо довгий текст питання
            question_text = question[2][:50] + \
                "..." if len(question[2]) > 50 else question[2]

            difficulty_text = {1: "Легкий", 2: "Середній",
                               3: "Важкий"}.get(question[5], "Невідомий")

            self.questions_tree.insert('', 'end', values=(
                question[0],  # ID
                question[1],  # Категорія
                question_text,  # Питання (обрізане)
                question[3],  # Тип
                difficulty_text,  # Складність
                question[6] or 0  # Використання
            ))

    def add_question_dialog(self):
        """Діалог додавання питання"""
        self.question_dialog(mode='add')

    def edit_question_dialog(self):
        """Діалог редагування питання"""
        selected = self.questions_tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Оберіть питання для редагування")
            return

        question_id = self.questions_tree.item(selected[0])['values'][0]
        self.question_dialog(mode='edit', question_id=question_id)

    def question_dialog(self, mode='add', question_id=None):
        """Універсальний діалог для питань"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Додати питання" if mode ==
                     'add' else "Редагувати питання")
        dialog.geometry("600x700")
        dialog.configure(bg='#f0f0f0')

        # Отримуємо категорії
        categories = self.question_manager.get_categories()

        # Якщо редагуємо, отримуємо дані питання
        if mode == 'edit' and question_id:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category_id, question_text, question_type, correct_answer, 
                       options, difficulty, explanation
                FROM questions WHERE id = ?
            ''', (question_id,))
            question_data = cursor.fetchone()
            conn.close()
        else:
            question_data = None

        # Форма
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Категорія
        ttk.Label(main_frame, text="Категорія:").pack(anchor='w')
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            main_frame, textvariable=category_var, state='readonly')
        category_combo['values'] = [
            f"{cat[0]} - {cat[1]}" for cat in categories]
        category_combo.pack(fill='x', pady=(0, 10))

        if question_data:
            for i, cat in enumerate(categories):
                if cat[0] == question_data[0]:
                    category_combo.current(i)
                    break

        # Текст питання
        ttk.Label(main_frame, text="Текст питання:").pack(anchor='w')
        question_text = scrolledtext.ScrolledText(
            main_frame, height=4, wrap=tk.WORD)
        question_text.pack(fill='x', pady=(0, 10))

        if question_data:
            question_text.insert('1.0', question_data[1])

        # Тип питання
        ttk.Label(main_frame, text="Тип питання:").pack(anchor='w')
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(
            main_frame, textvariable=type_var, state='readonly')
        type_combo['values'] = ['multiple_choice', 'true_false', 'text_input']
        type_combo.pack(fill='x', pady=(0, 10))
        type_combo.bind('<<ComboboxSelected>>',
                        lambda e: self.update_options_frame())

        if question_data:
            type_combo.set(question_data[2])

        # Правильна відповідь
        ttk.Label(main_frame, text="Правильна відповідь:").pack(anchor='w')
        correct_answer_entry = ttk.Entry(main_frame)
        correct_answer_entry.pack(fill='x', pady=(0, 10))

        if question_data:
            correct_answer_entry.insert(0, question_data[3])

        # Варіанти відповідей (для множинного вибору)
        options_frame = ttk.LabelFrame(
            main_frame, text="Варіанти відповідей", padding="10")
        options_frame.pack(fill='x', pady=(0, 10))

        self.option_entries = []
        for i in range(4):
            ttk.Label(options_frame, text=f"Варіант {i+1}:").pack(anchor='w')
            entry = ttk.Entry(options_frame)
            entry.pack(fill='x', pady=(0, 5))
            self.option_entries.append(entry)

        if question_data and question_data[4]:
            options = json.loads(question_data[4])
            for i, option in enumerate(options[:4]):
                if i < len(self.option_entries):
                    self.option_entries[i].insert(0, option)

        # Складність
        ttk.Label(main_frame, text="Складність:").pack(anchor='w')
        difficulty_var = tk.IntVar()
        difficulty_frame = ttk.Frame(main_frame)
        difficulty_frame.pack(fill='x', pady=(0, 10))

        ttk.Radiobutton(difficulty_frame, text="Легкий",
                        variable=difficulty_var, value=1).pack(side='left')
        ttk.Radiobutton(difficulty_frame, text="Середній",
                        variable=difficulty_var, value=2).pack(side='left')
        ttk.Radiobutton(difficulty_frame, text="Важкий",
                        variable=difficulty_var, value=3).pack(side='left')

        if question_data:
            difficulty_var.set(question_data[5])
        else:
            difficulty_var.set(1)

        # Пояснення
        ttk.Label(main_frame, text="Пояснення:").pack(anchor='w')
        explanation_text = scrolledtext.ScrolledText(
            main_frame, height=3, wrap=tk.WORD)
        explanation_text.pack(fill='x', pady=(0, 10))

        if question_data:
            explanation_text.insert('1.0', question_data[6] or '')

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)

        def save_question():
            # Валідація
            if not category_var.get() or not question_text.get('1.0', 'end').strip():
                messagebox.showerror("Помилка", "Заповніть обов'язкові поля")
                return

            # Отримуємо дані
            category_id = int(category_var.get().split(' - ')[0])
            q_text = question_text.get('1.0', 'end').strip()
            q_type = type_var.get()
            correct_ans = correct_answer_entry.get().strip()
            difficulty = difficulty_var.get()
            explanation = explanation_text.get('1.0', 'end').strip()

            # Варіанти відповідей
            options = []
            if q_type == 'multiple_choice':
                options = [entry.get().strip()
                           for entry in self.option_entries if entry.get().strip()]
                if len(options) < 2:
                    messagebox.showerror(
                        "Помилка", "Для множинного вибору потрібно мінімум 2 варіанти")
                    return

            # Збереження
            if mode == 'add':
                success = self.question_manager.add_question(
                    category_id, q_text, q_type, correct_ans, options, difficulty, explanation
                )
            else:
                success = self.question_manager.update_question(
                    question_id, category_id, q_text, q_type, correct_ans, options, difficulty, explanation
                )

            if success:
                messagebox.showinfo("Успіх", "Питання збережено")
                dialog.destroy()
                self.refresh_questions()
            else:
                messagebox.showerror("Помилка", "Не вдалося зберегти питання")

        ttk.Button(button_frame, text="Зберегти",
                   command=save_question).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Скасувати",
                   command=dialog.destroy).pack(side='left')

        # Функція оновлення фрейму опцій
        def update_options_frame():
            if type_var.get() == 'multiple_choice':
                options_frame.pack(fill='x', pady=(0, 10))
            else:
                options_frame.pack_forget()

        self.update_options_frame = update_options_frame
        update_options_frame()  # Початкове оновлення

    def delete_question(self):
        """Видалення питання"""
        selected = self.questions_tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Оберіть питання для видалення")
            return

        if messagebox.askyesno("Підтвердження", "Ви впевнені, що хочете видалити це питання?"):
            question_id = self.questions_tree.item(selected[0])['values'][0]

            if self.question_manager.delete_question(question_id):
                messagebox.showinfo("Успіх", "Питання видалено")
                self.refresh_questions()
            else:
                messagebox.showerror("Помилка", "Не вдалося видалити питання")

    def add_category_dialog(self):
        """Діалог додавання категорії"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Додати категорію")
        dialog.geometry("400x300")
        dialog.configure(bg='#f0f0f0')

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill='both', expand=True)

        ttk.Label(main_frame, text="Назва категорії:").pack(anchor='w')
        name_entry = ttk.Entry(main_frame)
        name_entry.pack(fill='x', pady=(0, 10))

        ttk.Label(main_frame, text="Опис:").pack(anchor='w')
        desc_text = scrolledtext.ScrolledText(
            main_frame, height=5, wrap=tk.WORD)
        desc_text.pack(fill='both', expand=True, pady=(0, 10))

        def save_category():
            name = name_entry.get().strip()
            description = desc_text.get('1.0', 'end').strip()

            if not name:
                messagebox.showerror("Помилка", "Введіть назву категорії")
                return

            if self.question_manager.add_category(name, description):
                messagebox.showinfo("Успіх", "Категорію додано")
                dialog.destroy()
            else:
                messagebox.showerror("Помилка", "Не вдалося додати категорію")

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Зберегти",
                   command=save_category).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Скасувати",
                   command=dialog.destroy).pack(side='left')

    def show_user_management(self):
        """Управління користувачами"""
        self.clear_work_frame()

        ttk.Label(self.work_frame, text="Управління користувачами",
                  font=('Arial', 14, 'bold')).pack(pady=10)

        # Панель кнопок
        button_frame = ttk.Frame(self.work_frame)
        button_frame.pack(fill='x', pady=5)

        ttk.Button(button_frame, text="Переглянути деталі",
                   command=self.view_user_details).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Змінити статус адміна",
                   command=self.toggle_admin_status).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Видалити користувача",
                   command=self.delete_user).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Оновити",
                   command=self.refresh_users).pack(side='left', padx=5)

        # Таблиця користувачів
        table_frame = ttk.Frame(self.work_frame)
        table_frame.pack(fill='both', expand=True, pady=10)

        columns = ('ID', 'Користувач', 'Email', 'Реєстрація',
                   'Адмін', 'Тестів', 'Середній бал')
        self.users_tree = ttk.Treeview(
            table_frame, columns=columns, show='headings', height=20)

        for col in columns:
            self.users_tree.heading(col, text=col)

        self.users_tree.column('ID', width=50)
        self.users_tree.column('Користувач', width=150)
        self.users_tree.column('Email', width=200)
        self.users_tree.column('Реєстрація', width=150)
        self.users_tree.column('Адмін', width=80)
        self.users_tree.column('Тестів', width=80)
        self.users_tree.column('Середній бал', width=120)

        scrollbar_u = ttk.Scrollbar(
            table_frame, orient='vertical', command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar_u.set)

        self.users_tree.pack(side='left', fill='both', expand=True)
        scrollbar_u.pack(side='right', fill='y')

        self.refresh_users()

    def refresh_users(self):
        """Оновлення списку користувачів"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        users = self.user_manager.get_all_users()

        for user in users:
            avg_score = round(user[6], 1) if user[6] else 0

            self.users_tree.insert('', 'end', values=(
                user[0],  # ID
                user[1],  # Username
                user[2] or '',  # Email
                user[3][:10],  # Registration date (тільки дата)
                'Так' if user[4] else 'Ні',  # Is admin
                user[5],  # Tests count
                f"{avg_score}%"  # Average score
            ))

    def view_user_details(self):
        """Перегляд деталей користувача"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Оберіть користувача")
            return

        user_id = self.users_tree.item(selected[0])['values'][0]
        username = self.users_tree.item(selected[0])['values'][1]

        # Створюємо вікно деталей
        details_window = tk.Toplevel(self.window)
        details_window.title(f"Деталі користувача: {username}")
        details_window.geometry("800x600")

        # Отримуємо статистику
        stats = self.user_manager.get_user_statistics(user_id)

        main_frame = ttk.Frame(details_window, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Загальна статистика
        general_frame = ttk.LabelFrame(
            main_frame, text="Загальна статистика", padding="10")
        general_frame.pack(fill='x', pady=5)

        if stats['general'][0] > 0:
            ttk.Label(general_frame, text=f"Всього тестів: {stats['general'][0]}").pack(
                anchor='w')
            ttk.Label(general_frame, text=f"Всього питань: {stats['general'][1]}").pack(
                anchor='w')
            ttk.Label(general_frame, text=f"Правильних відповідей: {stats['general'][2]}").pack(
                anchor='w')
            ttk.Label(general_frame, text=f"Загальний час: {stats['general'][3]} сек").pack(
                anchor='w')
            ttk.Label(general_frame, text=f"Середній відсоток: {stats['general'][4]:.1f}%").pack(
                anchor='w')
        else:
            ttk.Label(general_frame,
                      text="Користувач ще не проходив тести").pack()

        # Статистика по категоріях
        if stats['categories']:
            cat_frame = ttk.LabelFrame(
                main_frame, text="Статистика по категоріях", padding="10")
            cat_frame.pack(fill='both', expand=True, pady=5)

            cat_tree = ttk.Treeview(cat_frame, columns=(
                'Категорія', 'Тестів', 'Середній бал'), show='headings')
            cat_tree.heading('Категорія', text='Категорія')
            cat_tree.heading('Тестів', text='Тестів')
            cat_tree.heading('Середній бал', text='Середній бал')

            for cat_stat in stats['categories']:
                cat_tree.insert('', 'end', values=(
                    cat_stat[0], cat_stat[1], f"{cat_stat[2]:.1f}%"
                ))

            cat_tree.pack(fill='both', expand=True)

        # Останні тести
        if stats['recent_tests']:
            recent_frame = ttk.LabelFrame(
                main_frame, text="Останні тести", padding="10")
            recent_frame.pack(fill='both', expand=True, pady=5)

            recent_tree = ttk.Treeview(recent_frame, columns=(
                'Категорія', 'Дата', 'Результат'), show='headings')
            recent_tree.heading('Категорія', text='Категорія')
            recent_tree.heading('Дата', text='Дата')
            recent_tree.heading('Результат', text='Результат')

            for test in stats['recent_tests']:
                recent_tree.insert('', 'end', values=(
                    test[0], test[1][:
                                     16], f"{test[2]}/{test[3]} ({test[4]:.1f}%)"
                ))

            recent_tree.pack(fill='both', expand=True)

    def toggle_admin_status(self):
        """Зміна статусу адміністратора"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Оберіть користувача")
            return

        user_id = self.users_tree.item(selected[0])['values'][0]
        username = self.users_tree.item(selected[0])['values'][1]
        current_status = self.users_tree.item(selected[0])['values'][4]

        new_status = "звичайного користувача" if current_status == "Так" else "адміністратора"

        if messagebox.askyesno("Підтвердження",
                               f"Змінити статус користувача {username} на {new_status}?"):
            if self.user_manager.toggle_admin_status(user_id):
                messagebox.showinfo("Успіх", "Статус змінено")
                self.refresh_users()
            else:
                messagebox.showerror("Помилка", "Не вдалося змінити статус")

    def delete_user(self):
        """Видалення користувача"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Увага", "Оберіть користувача")
            return

        user_id = self.users_tree.item(selected[0])['values'][0]
        username = self.users_tree.item(selected[0])['values'][1]

        if user_id == self.current_user.user_id:
            messagebox.showerror("Помилка", "Не можна видалити власний акаунт")
            return

        if messagebox.askyesno("Підтвердження",
                               f"Ви впевнені, що хочете видалити користувача {username}?\n"
                               "Це також видалить всі його результати тестів."):
            if self.user_manager.delete_user(user_id):
                messagebox.showinfo("Успіх", "Користувача видалено")
                self.refresh_users()
            else:
                messagebox.showerror(
                    "Помилка", "Не вдалося видалити користувача")

    def show_system_statistics(self):
        """Показ системної статистики"""
        self.clear_work_frame()

        ttk.Label(self.work_frame, text="Статистика системи",
                  font=('Arial', 14, 'bold')).pack(pady=10)

        # Отримуємо статистику
        stats = self.statistics.get_general_statistics()

        # Створюємо notebook для вкладок
        notebook = ttk.Notebook(self.work_frame)
        notebook.pack(fill='both', expand=True)

        # Вкладка загальної статистики
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="Загальна статистика")

        # Статистичні картки
        cards_frame = ttk.Frame(general_frame)
        cards_frame.pack(fill='x', padx=20, pady=20)

        # Створюємо картки
        self.create_stat_card(cards_frame, "Користувачі", stats['general']['total_users'],
                              f"Адмінів: {stats['general']['admin_users']}")
        self.create_stat_card(cards_frame, "Питання", stats['general']['total_questions'],
                              f"Категорій: {stats['general']['total_categories']}")
        self.create_stat_card(cards_frame, "Тести", stats['general']['total_tests'],
                              f"Успішність: {stats['general']['avg_success_rate']}%")

        # Вкладка графіків
        charts_frame = ttk.Frame(notebook)
        notebook.add(charts_frame, text="Графіки")

        # Графік популярності категорій
        if stats['category_popularity']:
            self.create_category_chart(
                charts_frame, stats['category_popularity'])

        # Вкладка детальної статистики
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="Деталі")

        # Таблиця популярності категорій
        if stats['category_popularity']:
            pop_frame = ttk.LabelFrame(
                details_frame, text="Популярність категорій", padding="10")
            pop_frame.pack(fill='x', padx=20, pady=10)

            pop_tree = ttk.Treeview(pop_frame, columns=(
                'Категорія', 'Тестів'), show='headings', height=8)
            pop_tree.heading('Категорія', text='Категорія')
            pop_tree.heading('Тестів', text='Кількість тестів')

            for cat_name, tests_count in stats['category_popularity']:
                pop_tree.insert('', 'end', values=(cat_name, tests_count))

            pop_tree.pack(fill='x')

        # Розподіл по складності
        if stats['difficulty_distribution']:
            diff_frame = ttk.LabelFrame(
                details_frame, text="Розподіл по складності", padding="10")
            diff_frame.pack(fill='x', padx=20, pady=10)

            diff_tree = ttk.Treeview(diff_frame, columns=(
                'Складність', 'Відповідей'), show='headings', height=5)
            diff_tree.heading('Складність', text='Рівень складності')
            diff_tree.heading('Відповідей', text='Кількість відповідей')

            difficulty_names = {1: "Легкий", 2: "Середній", 3: "Важкий"}
            for difficulty, count in stats['difficulty_distribution']:
                diff_tree.insert('', 'end', values=(difficulty_names.get(
                    difficulty, f"Рівень {difficulty}"), count))

            diff_tree.pack(fill='x')

    def create_stat_card(self, parent, title, value, subtitle):
        """Створення статистичної картки"""
        card = ttk.LabelFrame(parent, text=title, padding="15")
        card.pack(side='left', fill='both', expand=True, padx=10)

        ttk.Label(card, text=str(value), font=('Arial', 20, 'bold')).pack()
        ttk.Label(card, text=subtitle, font=('Arial', 9)).pack()

    def create_category_chart(self, parent, category_data):
        """Створення графіку популярності категорій"""
        chart_frame = ttk.LabelFrame(
            parent, text="Популярність категорій", padding="10")
        chart_frame.pack(fill='both', expand=True, padx=20, pady=20)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        categories = [item[0] for item in category_data]
        counts = [item[1] for item in category_data]

        # Стовпчикова діаграма
        ax1.bar(range(len(categories)), counts)
        ax1.set_title('Кількість тестів по категоріях')
        ax1.set_xlabel('Категорії')
        ax1.set_ylabel('Кількість тестів')
        ax1.set_xticks(range(len(categories)))
        ax1.set_xticklabels([cat[:10] + '...' if len(cat)
                            > 10 else cat for cat in categories], rotation=45)

        # Кругова діаграма
        ax2.pie(counts, labels=[cat[:15] + '...' if len(cat) >
                15 else cat for cat in categories], autopct='%1.1f%%')
        ax2.set_title('Розподіл тестів по категоріях')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_export_options(self):
        """Показ опцій експорту"""
        self.clear_work_frame()

        ttk.Label(self.work_frame, text="Експорт даних",
                  font=('Arial', 14, 'bold')).pack(pady=10)

        # Фрейм опцій експорту
        export_frame = ttk.LabelFrame(
            self.work_frame, text="Оберіть тип експорту", padding="20")
        export_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # CSV експорт
        csv_frame = ttk.LabelFrame(
            export_frame, text="Експорт у CSV", padding="15")
        csv_frame.pack(fill='x', pady=10)

        ttk.Button(csv_frame, text="Експорт користувачів",
                   command=lambda: self.export_csv('users')).pack(side='left', padx=5)
        ttk.Button(csv_frame, text="Експорт питань",
                   command=lambda: self.export_csv('questions')).pack(side='left', padx=5)
        ttk.Button(csv_frame, text="Експорт результатів",
                   command=lambda: self.export_csv('results')).pack(side='left', padx=5)

        # JSON експорт
        json_frame = ttk.LabelFrame(
            export_frame, text="Експорт у JSON", padding="15")
        json_frame.pack(fill='x', pady=10)

        ttk.Button(json_frame, text="Повний бекап системи",
                   command=lambda: self.export_json('full_backup')).pack(side='left', padx=5)

        # PDF звіти
        pdf_frame = ttk.LabelFrame(
            export_frame, text="PDF звіти", padding="15")
        pdf_frame.pack(fill='x', pady=10)

        ttk.Button(pdf_frame, text="Звіт про стан системи",
                   command=lambda: self.export_pdf('system_report')).pack(side='left', padx=5)

        # Статус експорту
        self.export_status = ttk.Label(
            export_frame, text="", foreground='green')
        self.export_status.pack(pady=20)

    def export_csv(self, data_type):
        """Експорт даних у CSV"""
        filename = filedialog.asksaveasfilename(
            title=f"Зберегти {data_type} як CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            if self.exporter.export_to_csv(data_type, filename):
                self.export_status.config(
                    text=f"✅ {data_type} успішно експортовано в {filename}")
            else:
                self.export_status.config(
                    text=f"❌ Помилка експорту {data_type}", foreground='red')

    def export_json(self, data_type):
        """Експорт даних у JSON"""
        filename = filedialog.asksaveasfilename(
            title=f"Зберегти {data_type} як JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            if self.exporter.export_to_json(data_type, filename):
                self.export_status.config(
                    text=f"✅ {data_type} успішно експортовано в {filename}")
            else:
                self.export_status.config(
                    text=f"❌ Помилка експорту {data_type}", foreground='red')

    def export_pdf(self, report_type):
        """Експорт звіту у PDF"""
        filename = filedialog.asksaveasfilename(
            title=f"Зберегти {report_type} як PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if filename:
            if self.exporter.export_to_pdf(report_type, filename):
                self.export_status.config(
                    text=f"✅ {report_type} успішно експортовано в {filename}")
            else:
                self.export_status.config(
                    text=f"❌ Помилка експорту {report_type}", foreground='red')

# Інтеграція з основним додатком


def show_admin_panel_enhanced(parent, db_name: str, current_user):
    """Показ розширеної адміністративної панелі"""
    if not current_user.is_admin:
        messagebox.showerror("Помилка", "Доступ заборонено")
        return

    admin_panel = AdminPanelGUI(parent, db_name, current_user)
    return admin_panel
