import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import mss


# Функция для захвата экрана УЗИ
def capture_screen():
    with mss.mss() as sct:
        screen = sct.grab(sct.monitors[2])  # Захват экрана второго монитора
        img = Image.frombytes("RGB", (screen.width, screen.height), screen.rgb)
        return img


# Функция для уменьшения прозрачности изображения
def reduce_transparency(img, alpha_value=0.5):
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda i: int(i * alpha_value))
    img = Image.merge('RGBA', (r, g, b, a))
    return img


# Функция для добавления каркаса на изображение
def add_frame_mask(img, mask_path):
    mask_img = Image.open(mask_path).convert("RGBA")
    mask_img = reduce_transparency(mask_img, alpha_value=0.5)

    img_width, img_height = img.size
    mask_width, mask_height = mask_img.size
    position = ((img_width - mask_width) // 2, (img_height - mask_height) // 2)

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


# Функция для выбора каркаса на основе характеристик
def get_frame_path():
    gender = gender_var.get()
    body_type = body_type_var.get()
    height = height_var.get()

    # Выбираем каркас на основе характеристик
    if gender == "Мужчина" and body_type == "Худой" and height == "Высокий":
        return "mask_female_fat_short.jpg"
    elif gender == "Женщина" and body_type == "Толстый" and height == "Низкий":
        return "mask_male_thin_tall.png"
    # Добавьте другие условия в зависимости от ваших изображений каркасов
    return "mask_male_thin_tall.png"


# Функция для запуска трансляции
def start_stream():
    mask_path = get_frame_path()  # Получаем путь к каркасу на основе фильтров
    messagebox.showinfo("Трансляция", f"Начинаем трансляцию с каркасом: {mask_path}")

    # Скрываем элементы фильтрации
    filter_frame.pack_forget()

    # Запускаем трансляцию
    update_image(mask_path)


# Создаем главное окно приложения
root = tk.Tk()
root.title("УЗИ с выбором каркаса")

# Устанавливаем размер окна
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")

# Создаем фрейм для фильтров
filter_frame = tk.Frame(root)
filter_frame.pack(pady=20)

# Переменные для фильтров
gender_var = tk.StringVar(value="Мужчина")
body_type_var = tk.StringVar(value="Худой")
height_var = tk.StringVar(value="Высокий")

# Элементы для выбора характеристик с использованием Combobox
tk.Label(filter_frame, text="Пол:").grid(row=0, column=0, padx=10, pady=5)
gender_combobox = ttk.Combobox(filter_frame, textvariable=gender_var, values=["Мужчина", "Женщина"])
gender_combobox.grid(row=0, column=1, padx=10, pady=5)

tk.Label(filter_frame, text="Тип телосложения:").grid(row=1, column=0, padx=10, pady=5)
body_type_combobox = ttk.Combobox(filter_frame, textvariable=body_type_var, values=["Худой", "Толстый"])
body_type_combobox.grid(row=1, column=1, padx=10, pady=5)

tk.Label(filter_frame, text="Рост:").grid(row=2, column=0, padx=10, pady=5)
height_combobox = ttk.Combobox(filter_frame, textvariable=height_var, values=["Высокий", "Низкий"])
height_combobox.grid(row=2, column=1, padx=10, pady=5)

# Кнопка для запуска трансляции
start_button = tk.Button(filter_frame, text="Начать трансляцию", command=start_stream)
start_button.grid(row=3, column=0, columnspan=2, pady=20)

# Метка для отображения изображения
label = tk.Label(root)
label.pack()

# Запуск приложения
root.mainloop()
