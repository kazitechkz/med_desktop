import tkinter as tk
from PIL import Image, ImageTk
import mss
import numpy as np


# Функция для захвата экрана
def capture_screen():
    with mss.mss() as sct:
        # Захват всего экрана
        screen = sct.grab(sct.monitors[2])  # Монитор 1
        img = Image.frombytes("RGB", (screen.width, screen.height), screen.rgb)
        return img


# Функция для обновления изображения в окне
def update_image():
    # Захватываем экран
    img = capture_screen()

    # Конвертируем изображение в формат, совместимый с tkinter
    img_tk = ImageTk.PhotoImage(img)

    # Обновляем изображение в метке (label)
    label.config(image=img_tk)
    label.image = img_tk

    # Повторяем обновление через 50 миллисекунд
    root.after(50, update_image)


# Создаем окно с tkinter
root = tk.Tk()
root.title("Screen Capture")

# Создаем метку для отображения изображения
label = tk.Label(root)
label.pack()

# Запускаем процесс обновления изображения
update_image()

# Запуск приложения
root.mainloop()
