"""
Скрипт для автоматичного встановлення залежностей
"""

import subprocess
import sys
import os


def install_package(package):
    """Встановлення пакету через pip"""
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} успішно встановлено")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Помилка встановлення {package}")
        return False


def check_package(package):
    """Перевірка чи встановлений пакет"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False


def main():
    """Головна функція встановлення"""
    print("Перевірка та встановлення залежностей для Тренажера з Інформатики")
    print("=" * 70)

    # Список необхідних пакетів
    required_packages = [
        ("matplotlib", "matplotlib"),
        ("pandas", "pandas"),
        ("reportlab", "reportlab"),
        ("Pillow", "PIL"),
        ("mysql-connector-python", "mysql.connector")
    ]

    # Стандартні пакети Python (не потребують встановлення)
    standard_packages = [
        "tkinter", "sqlite3", "json", "hashlib", "datetime",
        "csv", "os", "sys", "logging"
    ]

    print("Перевірка стандартних пакетів Python:")
    for package in standard_packages:
        if check_package(package):
            print(f"✅ {package} - доступний")
        else:
            print(f"❌ {package} - недоступний (можливо потрібно оновити Python)")

    print("\n Перевірка та встановлення додаткових пакетів:")

    failed_packages = []

    for pip_name, import_name in required_packages:
        if check_package(import_name):
            print(f"✅ {pip_name} - вже встановлено")
        else:
            print(f"⏳ Встановлення {pip_name}...")
            if not install_package(pip_name):
                failed_packages.append(pip_name)

    print("\n" + "=" * 70)

    if failed_packages:
        print("❌ Деякі пакети не вдалося встановити:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n💡 Спробуйте встановити їх вручну:")
        for package in failed_packages:
            print(f"   pip install {package}")
        print("\n⚠️  Програма може працювати з обмеженим функціоналом")
    else:
        print("✅ Всі залежності успішно встановлені!")
        print("Тепер ви можете запустити програму: python main_enhanced.py")

    print("\n📋 Додаткова інформація:")
    print("   - Для повного функціоналу рекомендується Python 3.8+")
    print("   - Для MySQL підтримки встановіть MySQL Server")
    print("   - Для експорту PDF потрібен reportlab")
    print("   - Для графіків потрібен matplotlib")


if __name__ == "__main__":
    main()
