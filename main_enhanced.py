"""
Оновлена версія головного файлу з інтегрованою адміністративною панеллю
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import hashlib
import datetime
import json
import random
from typing import Dict, List, Tuple, Optional
from admin_panel import AdminPanelGUI

# Імпортуємо всі класи з оригінального main.py
from main import (
    DatabaseManager, User, Question, AuthenticationManager,
    TestManager, InformaticsTrainerGUI
)


class EnhancedInformaticsTrainerGUI(InformaticsTrainerGUI):
    """Розширена версія GUI з інтегрованою адміністративною панеллю"""

    def __init__(self):
        super().__init__()
        self.admin_panel = None

    def show_admin_panel(self):
        """Показ розширеної адміністративної панелі"""
        if not self.auth_manager.current_user.is_admin:
            messagebox.showerror("Помилка", "Доступ заборонено")
            return

        # Закриваємо попередню панель якщо вона відкрита
        if self.admin_panel and hasattr(self.admin_panel, 'window'):
            try:
                self.admin_panel.window.destroy()
            except:
                pass

        # Створюємо нову панель
        self.admin_panel = AdminPanelGUI(
            self.root,
            self.db_manager.db_name,
            self.auth_manager.current_user
        )

    def show_question_management(self):
        """Перенаправлення на розширене управління питаннями"""
        self.show_admin_panel()
        if self.admin_panel:
            self.admin_panel.show_question_management()

    def show_user_management(self):
        """Перенаправлення на розширене управління користувачами"""
        self.show_admin_panel()
        if self.admin_panel:
            self.admin_panel.show_user_management()

    def show_system_statistics(self):
        """Перенаправлення на розширену системну статистику"""
        self.show_admin_panel()
        if self.admin_panel:
            self.admin_panel.show_system_statistics()

    def export_data(self):
        """Перенаправлення на розширений експорт даних"""
        self.show_admin_panel()
        if self.admin_panel:
            self.admin_panel.show_export_options()


if __name__ == "__main__":
    app = EnhancedInformaticsTrainerGUI()
    app.run()
