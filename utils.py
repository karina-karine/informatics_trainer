"""
Допоміжні функції та утиліти для програми-тренажера
"""

import hashlib
import secrets
import string
import datetime
import json
import os
import logging
from typing import Dict, List, Any, Optional
import tkinter as tk
from tkinter import messagebox, filedialog


class SecurityUtils:
    """Утиліти для безпеки"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Хешування паролю"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Перевірка паролю"""
        return SecurityUtils.hash_password(password) == hashed

    @staticmethod
    def generate_session_token() -> str:
        """Генерація токену сесії"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Перевірка складності паролю"""
        result = {
            'is_valid': True,
            'errors': [],
            'score': 0
        }

        if len(password) < 6:
            result['errors'].append(
                "Пароль повинен містити мінімум 6 символів")
            result['is_valid'] = False
        else:
            result['score'] += 1

        if any(c.isupper() for c in password):
            result['score'] += 1

        if any(c.islower() for c in password):
            result['score'] += 1

        if any(c.isdigit() for c in password):
            result['score'] += 1

        if any(c in string.punctuation for c in password):
            result['score'] += 1

        return result


class DataUtils:
    """Утиліти для роботи з даними"""

    @staticmethod
    def export_to_json(data: Any, filename: str) -> bool:
        """Експорт даних в JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            logging.error(f"Помилка експорту в JSON: {e}")
            return False

    @staticmethod
    def import_from_json(filename: str) -> Optional[Any]:
        """Імпорт даних з JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Помилка імпорту з JSON: {e}")
            return None

    @staticmethod
    def calculate_statistics(results: List[Dict]) -> Dict[str, Any]:
        """Розрахунок статистики"""
        if not results:
            return {}

        total_tests = len(results)
        total_questions = sum(r.get('total_questions', 0) for r in results)
        total_correct = sum(r.get('correct_answers', 0) for r in results)
        total_time = sum(r.get('time_spent', 0) for r in results)

        avg_percentage = (total_correct / total_questions *
                          100) if total_questions > 0 else 0
        avg_time_per_question = (
            total_time / total_questions) if total_questions > 0 else 0

        return {
            'total_tests': total_tests,
            'total_questions': total_questions,
            'total_correct': total_correct,
            'average_percentage': round(avg_percentage, 2),
            'total_time': total_time,
            'average_time_per_question': round(avg_time_per_question, 2)
        }


class UIUtils:
    """Утиліти для інтерфейсу користувача"""

    @staticmethod
    def center_window(window: tk.Tk, width: int, height: int):
        """Центрування вікна на екрані"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def show_info_dialog(title: str, message: str):
        """Показ інформаційного діалогу"""
        messagebox.showinfo(title, message)

    @staticmethod
    def show_error_dialog(title: str, message: str):
        """Показ діалогу помилки"""
        messagebox.showerror(title, message)

    @staticmethod
    def show_warning_dialog(title: str, message: str):
        """Показ діалогу попередження"""
        messagebox.showwarning(title, message)

    @staticmethod
    def ask_yes_no(title: str, message: str) -> bool:
        """Діалог підтвердження"""
        return messagebox.askyesno(title, message)

    @staticmethod
    def select_file(title: str, filetypes: List[tuple]) -> Optional[str]:
        """Діалог вибору файлу"""
        return filedialog.askopenfilename(title=title, filetypes=filetypes)

    @staticmethod
    def select_save_file(title: str, filetypes: List[tuple]) -> Optional[str]:
        """Діалог збереження файлу"""
        return filedialog.asksaveasfilename(title=title, filetypes=filetypes)


class LoggingUtils:
    """Утиліти для логування"""

    @staticmethod
    def setup_logging(log_file: str = "informatics_trainer.log", level: str = "INFO"):
        """Налаштування системи логування"""
        log_level = getattr(logging, level.upper(), logging.INFO)

        # Створюємо директорію для логів
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Налаштування форматування
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Обробник для файлу
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)

        # Обробник для консолі
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)

        # Налаштування кореневого логера
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        return root_logger

    @staticmethod
    def log_user_action(user_id: int, action: str, details: str = ""):
        """Логування дій користувача"""
        logger = logging.getLogger("user_actions")
        logger.info(f"User {user_id}: {action} - {details}")


class ValidationUtils:
    """Утиліти для валідації"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Валідація email адреси"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_username(username: str) -> Dict[str, Any]:
        """Валідація імені користувача"""
        result = {'is_valid': True, 'errors': []}

        if len(username) < 3:
            result['errors'].append(
                "Ім'я користувача повинно містити мінімум 3 символи")
            result['is_valid'] = False

        if len(username) > 50:
            result['errors'].append(
                "Ім'я користувача не може містити більше 50 символів")
            result['is_valid'] = False

        if not username.replace('_', '').replace('-', '').isalnum():
            result['errors'].append(
                "Ім'я користувача може містити тільки літери, цифри, _ та -")
            result['is_valid'] = False

        return result

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Очищення вхідного тексту"""
        # Видаляємо потенційно небезпечні символи
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        for char in dangerous_chars:
            text = text.replace(char, '')

        return text.strip()


class FileUtils:
    """Утиліти для роботи з файлами"""

    @staticmethod
    def ensure_directory_exists(directory: str):
        """Створення директорії якщо вона не існує"""
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def get_file_size(filepath: str) -> int:
        """Отримання розміру файлу в байтах"""
        try:
            return os.path.getsize(filepath)
        except OSError:
            return 0

    @staticmethod
    def backup_file(filepath: str, backup_dir: str = "backups") -> bool:
        """Створення резервної копії файлу"""
        try:
            FileUtils.ensure_directory_exists(backup_dir)

            filename = os.path.basename(filepath)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{timestamp}_{filename}"
            backup_path = os.path.join(backup_dir, backup_filename)

            import shutil
            shutil.copy2(filepath, backup_path)
            return True
        except Exception as e:
            logging.error(f"Помилка створення резервної копії: {e}")
            return False

    @staticmethod
    def clean_old_backups(backup_dir: str, max_age_days: int = 30):
        """Очищення старих резервних копій"""
        try:
            if not os.path.exists(backup_dir):
                return

            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=max_age_days)

            for filename in os.listdir(backup_dir):
                filepath = os.path.join(backup_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.datetime.fromtimestamp(
                        os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        logging.info(
                            f"Видалено стару резервну копію: {filename}")
        except Exception as e:
            logging.error(f"Помилка очищення старих резервних копій: {e}")


class TestUtils:
    """Утиліти для тестування"""

    @staticmethod
    def shuffle_questions(questions: List[Any]) -> List[Any]:
        """Перемішування питань"""
        import random
        shuffled = questions.copy()
        random.shuffle(shuffled)
        return shuffled

    @staticmethod
    def shuffle_options(options: List[str]) -> List[str]:
        """Перемішування варіантів відповідей"""
        import random
        shuffled = options.copy()
        random.shuffle(shuffled)
        return shuffled

    @staticmethod
    def calculate_score(correct_answers: int, total_questions: int, time_spent: int) -> float:
        """Розрахунок балу з урахуванням часу"""
        if total_questions == 0:
            return 0.0

        base_score = (correct_answers / total_questions) * 100

        # Бонус за швидкість (максимум 10% додаткових балів)
        avg_time_per_question = time_spent / total_questions
        if avg_time_per_question < 30:  # Менше 30 секунд на питання
            time_bonus = min(10, (30 - avg_time_per_question) / 3)
            base_score += time_bonus

        return min(100.0, round(base_score, 2))

    @staticmethod
    def get_difficulty_description(difficulty: int) -> str:
        """Отримання опису складності"""
        descriptions = {
            1: "Легкий",
            2: "Середній",
            3: "Важкий"
        }
        return descriptions.get(difficulty, "Невідомий")

    @staticmethod
    def format_time(seconds: int) -> str:
        """Форматування часу в читабельний вигляд"""
        if seconds < 60:
            return f"{seconds} сек"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes} хв {remaining_seconds} сек"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            return f"{hours} год {remaining_minutes} хв"


# Ініціалізація логування при імпорті модуля
LoggingUtils.setup_logging()
