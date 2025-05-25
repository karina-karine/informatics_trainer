#!/usr/bin/env python3
"""
Головний файл для запуску програми-тренажера з інформатики
"""

import sys
import os
import logging
from pathlib import Path

# Додаємо поточну директорію до шляху Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from main import InformaticsTrainerGUI
    from config import config
    from utils import LoggingUtils, FileUtils
except ImportError as e:
    print(f"Помилка імпорту: {e}")
    print("Переконайтеся, що всі необхідні файли знаходяться в одній директорії")
    sys.exit(1)


def setup_application():
    """Налаштування додатку перед запуском"""
    try:
        # Створюємо необхідні директорії
        config.create_directories()

        # Налаштовуємо логування
        LoggingUtils.setup_logging(
            log_file=os.path.join(config.PATHS['logs_dir'], 'app.log'),
            level=config.LOGGING_CONFIG['level']
        )

        logger = logging.getLogger(__name__)
        logger.info("Запуск програми-тренажера з інформатики")

        # Очищуємо старі резервні копії
        FileUtils.clean_old_backups(config.PATHS['backup_dir'])

        return True

    except Exception as e:
        print(f"Помилка налаштування додатку: {e}")
        return False


def main():
    """Головна функція"""
    print("=" * 60)
    print("    ПРОГРАМА-ТРЕНАЖЕР З ІНФОРМАТИКИ")
    print("=" * 60)
    print("Автор: ")
    print("Версія: 2.0")
    print("Курсова робота з розробки програм-тренажерів")
    print("=" * 60)

    # Налаштування додатку
    if not setup_application():
        print("Не вдалося налаштувати додаток. Завершення роботи.")
        return 1

    try:
        # Створюємо та запускаємо додаток
        app = InformaticsTrainerGUI()

        # Логуємо запуск
        logger = logging.getLogger(__name__)
        logger.info("Додаток успішно запущено")

        # Запускаємо головний цикл
        app.run()

        logger.info("Додаток завершено")
        return 0

    except KeyboardInterrupt:
        print("\nПрограма перервана користувачем")
        return 0

    except Exception as e:
        error_msg = f"Критична помилка: {e}"
        print(error_msg)

        # Логуємо помилку
        logger = logging.getLogger(__name__)
        logger.error(error_msg, exc_info=True)

        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
