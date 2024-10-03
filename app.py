import tkinter as tk
from views.main_view import MainView
from models.database import Database  # Импортируем класс Database для инициализации

# Запуск главного приложения
if __name__ == '__main__':
    # Инициализация базы данных перед запуском приложения
    db = Database()
    db.initialize_database()

    # Запуск интерфейса
    root = tk.Tk()
    app = MainView(root)
    root.mainloop()
