import tkinter as tk
from views.main_view import MainView

# Запуск главного приложения
if __name__ == '__main__':
    root = tk.Tk()
    app = MainView(root)
    root.mainloop()