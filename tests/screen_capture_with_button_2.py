import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mss

# Функция для захвата экрана
def capture_screen():
    with mss.mss() as sct:
        screen = sct.grab(sct.monitors[2])  # Захват экрана второго монитора (или первого, если это основной)
        img = Image.frombytes("RGB", (screen.width, screen.height), screen.rgb)
        return img

# Функция для обновления изображения на экране
def update_image():
    img = capture_screen()  # Захватываем экран
    img_tk = ImageTk.PhotoImage(img)  # Конвертируем изображение в формат tkinter
    label.config(image=img_tk)  # Обновляем картинку в метке
    label.image = img_tk  # Сохраняем ссылку на изображение для tkinter
    root.after(50, update_image)  # Повторяем каждые 50 мс

# Функция для запуска трансляции
def start_stream():
    messagebox.showinfo("Трансляция", "Начинаем трансляцию экрана!")
    update_image()  # Запускаем функцию обновления изображения

# Создаем главное окно приложения
root = tk.Tk()
root.title("Screen Capture Application")
root.geometry("800x600")

# Добавляем кнопку "Начать трансляцию"
start_button = tk.Button(root, text="Начать трансляцию", command=start_stream)
start_button.pack(pady=20)

# Добавляем метку для отображения экрана
label = tk.Label(root)
label.pack()

# Запуск приложения
root.mainloop()
