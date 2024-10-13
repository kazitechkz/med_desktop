import tkinter as tk

from views.cap_view import CapView
from models.database import Database  # Импортируем класс Database для инициализации

# Запуск главного приложения
if __name__ == '__main__':
    # Инициализация базы данных перед запуском приложения
    db = Database()
    db.initialize_database()

    # Запуск интерфейса
    root = tk.Tk()
    app = CapView(root)
    root.mainloop()
