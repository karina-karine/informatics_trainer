"""
Конфігураційний файл для програми-тренажера з інформатики
"""

import os
from typing import Dict, Any


class Config:
    """Клас конфігурації додатку"""

    # Налаштування бази даних
    DATABASE_CONFIG = {
        'sqlite': {
            'db_name': 'informatics_trainer.db',
            'backup_interval': 3600  # Резервне копіювання кожну годину
        },
        'mysql': {
            'host': 'localhost',
            'port': 3306,
            'database': 'informatics_trainer',
            'user': 'root',
            'password': '',
            'charset': 'utf8mb4'
        }
    }

    # Налаштування інтерфейсу
    UI_CONFIG = {
        'window_size': '800x600',
        'min_window_size': '600x400',
        'theme': 'clam',
        'font_family': 'Arial',
        'font_sizes': {
            'title': 16,
            'heading': 12,
            'normal': 10,
            'small': 8
        },
        'colors': {
            'primary': '#2196F3',
            'secondary': '#FFC107',
            'success': '#4CAF50',
            'error': '#F44336',
            'warning': '#FF9800',
            'background': '#f0f0f0'
        }
    }

    # Налаштування тестування
    TEST_CONFIG = {
        'default_questions_count': 10,
        'max_questions_count': 50,
        'time_limit_enabled': False,
        'time_limit_minutes': 30,
        'show_explanations': True,
        'shuffle_questions': True,
        'shuffle_answers': True,
        'difficulty_levels': {
            1: 'Легкий',
            2: 'Середній',
            3: 'Важкий'
        }
    }

    # Налаштування безпеки
    SECURITY_CONFIG = {
        'password_min_length': 6,
        'password_require_uppercase': False,
        'password_require_lowercase': False,
        'password_require_numbers': False,
        'password_require_special': False,
        'session_timeout_minutes': 60,
        'max_login_attempts': 5,
        'lockout_duration_minutes': 15
    }

    # Налаштування логування
    LOGGING_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'informatics_trainer.log',
        'max_file_size': 10 * 1024 * 1024,  # 10 MB
        'backup_count': 5
    }

    # Шляхи до файлів
    PATHS = {
        'data_dir': 'data',
        'backup_dir': 'backups',
        'export_dir': 'exports',
        'logs_dir': 'logs',
        'temp_dir': 'temp'
    }

    @classmethod
    def get_database_url(cls, db_type: str = 'sqlite') -> str:
        """Отримання URL бази даних"""
        if db_type == 'sqlite':
            return cls.DATABASE_CONFIG['sqlite']['db_name']
        elif db_type == 'mysql':
            config = cls.DATABASE_CONFIG['mysql']
            return f"mysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        else:
            raise ValueError(f"Непідтримуваний тип бази даних: {db_type}")

    @classmethod
    def create_directories(cls):
        """Створення необхідних директорій"""
        for path in cls.PATHS.values():
            os.makedirs(path, exist_ok=True)

    @classmethod
    def get_ui_setting(cls, setting_name: str, default: Any = None) -> Any:
        """Отримання налаштування інтерфейсу"""
        return cls.UI_CONFIG.get(setting_name, default)

    @classmethod
    def get_test_setting(cls, setting_name: str, default: Any = None) -> Any:
        """Отримання налаштування тестування"""
        return cls.TEST_CONFIG.get(setting_name, default)


# Глобальна конфігурація
config = Config()
