import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import mss


# Функция для захвата экрана УЗИ
def capture_screen():
    with mss.mss() as sct:
        # Захват экрана с УЗИ (например, второго монитора)
        screen = sct.grab(sct.monitors[2])  # Замените [1] на нужный номер монитора
        img = Image.frombytes("RGB", (screen.width, screen.height), screen.rgb)
        return img


# Функция для уменьшения прозрачности (увеличения прозрачности) изображения
def reduce_transparency(img, alpha_value=0.5):
    # Разделяем каналы изображения (R, G, B, A)
    img = img.convert("RGBA")
    r, g, b, a = img.split()

    # Применяем ко всем каналам одинаковую прозрачность
    a = a.point(lambda i: int(i * alpha_value))  # Уменьшаем непрозрачность

    # Объединяем каналы обратно
    img = Image.merge('RGBA', (r, g, b, a))
    return img


# Функция для добавления каркаса на изображение
def add_frame_mask(img, mask_path):
    # Загружаем каркас (маску правильной зоны расчета УЗИ)
    mask_img = Image.open(mask_path).convert("RGBA")

    # Уменьшаем непрозрачность каркаса
    mask_img = reduce_transparency(mask_img, alpha_value=0.7)  # Устанавливаем 30% прозрачности

    # Определяем позицию для наложения каркаса
    img_width, img_height = img.size
    mask_width, mask_height = mask_img.size
    position = ((img_width - mask_width) // 2, (img_height - mask_height) // 2)

    # Наложение каркаса на изображение
    img_with_frame = img.convert("RGBA")
    img_with_frame.paste(mask_img, position, mask_img)

    return img_with_frame.convert("RGB")


# Функция для обновления изображения с каркасом
def update_image(mask_path):
    img = capture_screen()  # Захватываем изображение с монитора УЗИ

    img_with_frame = add_frame_mask(img, mask_path)  # Накладываем каркас

    img_tk = ImageTk.PhotoImage(img_with_frame)  # Конвертируем для tkinter
    label.config(image=img_tk)  # Обновляем изображение в метке
    label.image = img_tk  # Сохраняем ссылку для tkinter
    root.after(50, update_image, mask_path)  # Повторяем каждые 50 мс


# Функция для запуска трансляции
def start_stream():
    mask_path = "../assets/masks/mask_female_fat_short.jpg"  # Замените на путь к вашему изображению-каркасу
    update_image(mask_path)


# Создаем окно приложения
root = tk.Tk()
root.title("УЗИ с каркасом правильной зоны")

# Устанавливаем размер окна
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

# Кнопка для запуска трансляции
start_button = tk.Button(root, text="Начать трансляцию", command=start_stream)
start_button.pack(pady=20)

# Метка для отображения изображения
label = tk.Label(root)
label.pack()

# Запуск приложения
root.mainloop()
