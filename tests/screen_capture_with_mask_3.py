import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import mss


# Функция для захвата экрана
def capture_screen():
    with mss.mss() as sct:
        screen = sct.grab(sct.monitors[2])  # Захват экрана второго монитора
        img = Image.frombytes("RGB", (screen.width, screen.height), screen.rgb)
        return img


# Функция для создания маски
def create_mask(img):
    # Создаем полупрозрачную маску
    mask = Image.new("RGBA", img.size, (255, 255, 255, 0))  # Прозрачный слой
    draw = ImageDraw.Draw(mask)

    # Рисуем прямоугольник с полупрозрачностью (например, на 30% прозрачности)
    draw.rectangle(((100, 100), (500, 500)), fill=(255, 0, 0, 128))  # Красный полупрозрачный квадрат

    # Наложение маски на изображение
    img_with_mask = Image.alpha_composite(img.convert("RGBA"), mask)
    return img_with_mask.convert("RGB")  # Возвращаем в формате RGB для отображения


# Функция для обновления изображения на экране
def update_image():
    img = capture_screen()  # Захватываем экран

    img_with_mask = create_mask(img)  # Добавляем маску

    img_tk = ImageTk.PhotoImage(img_with_mask)  # Конвертируем изображение в формат tkinter
    label.config(image=img_tk)  # Обновляем картинку в метке
    label.image = img_tk  # Сохраняем ссылку на изображение для tkinter
    root.after(50, update_image)  # Повторяем каждые 50 мс


# Функция для запуска трансляции
def start_stream():
    messagebox.showinfo("Трансляция", "Начинаем трансляцию экрана!")
    update_image()  # Запускаем функцию обновления изображения


# Создаем главное окно приложения
root = tk.Tk()
root.title("Screen Capture with Mask")

# Получаем разрешение экрана
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Устанавливаем размер окна на весь экран (с рамками)
root.geometry(f"{screen_width}x{screen_height}")

# Добавляем кнопку "Начать трансляцию"
start_button = tk.Button(root, text="Начать трансляцию", command=start_stream)
start_button.pack(pady=20)

# Добавляем метку для отображения экрана
label = tk.Label(root)
label.pack()

# Запуск приложения
root.mainloop()
