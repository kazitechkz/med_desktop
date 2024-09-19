import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import mss
import os
from datetime import datetime
import requests
import threading


# Функция для захвата экрана УЗИ (без маски)
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


# Функция для отправки скриншота на сервер
def upload_screenshot(file_path):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:5000/upload', files=files)  # URL сервера
            return response.status_code == 200
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
        return False


# Функция для сохранения скриншота и отправки его на сервер
def save_screenshot():
    img = capture_screen()  # Захватываем экран без маски

    # Создаем папку "screens", если она не существует
    if not os.path.exists("../screens"):
        os.makedirs("../screens")

    # Сохраняем изображение с текущей датой и временем
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"screens/screenshot_{timestamp}.png"
    img.save(file_path)
    print(f"Скриншот сохранен: {file_path}")

    # Показываем прелоадер
    preloader.pack(pady=10)
    info_label.config(text="Отправка скриншота на сервер...")

    # Отправляем скриншот на сервер в отдельном потоке
    def upload_thread():
        success = upload_screenshot(file_path)
        preloader.pack_forget()  # Убираем прелоадер
        if success:
            info_label.config(text="Скриншот успешно отправлен!", fg="green")
        else:
            info_label.config(text="Ошибка при отправке скриншота", fg="red")

    info_label.forget()
    threading.Thread(target=upload_thread).start()


# Функция для обновления изображения с каркасом
def update_image(mask_path):
    img = capture_screen()  # Захватываем изображение с монитора УЗИ

    img_with_frame = add_frame_mask(img, mask_path)  # Накладываем каркас

    # Изменяем размер изображения для правой части экрана (под размер трансляции)
    img_with_frame = img_with_frame.resize((right_frame.winfo_width(), right_frame.winfo_height()))

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


# Функция для обработки нажатий клавиш
def on_key_press(event):
    if event.keysym == "space":
        save_screenshot()  # Сохраняем скриншот при нажатии на пробел


# Функция для обновления информационной карточки
# def update_info_card():
#     # Имитация получения данных с сервера
#     response = requests.get('http://localhost:5000/data')  # URL сервера
#     if response.status_code == 200:
#         data = response.json()
#         info_label.config(text=f"Пациент: {data['name']}\nПол: {data['gender']}\nВозраст: {data['age']}")
#     root.after(5000, update_info_card)  # Обновляем данные каждые 5 секунд


# Создаем главное окно приложения
root = tk.Tk()
root.title("УЗИ с выбором каркаса и трансляцией")

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

# Создаем фрейм для информационной карточки и трансляции
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Левая часть экрана - информационная карточка
left_frame = tk.Frame(main_frame, width=300)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Метка для отображения информации
info_label = tk.Label(left_frame, text="Загрузка данных с сервера...", font=("Arial", 14), justify=tk.LEFT)
info_label.pack()

# Прелоадер для индикации отправки данных
preloader = ttk.Progressbar(left_frame, mode="indeterminate")
preloader.pack(pady=10)
preloader.pack_forget()  # Скрыть прелоадер по умолчанию

# Правая часть экрана - трансляция
right_frame = tk.Frame(main_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Метка для отображения изображения с УЗИ
label = tk.Label(right_frame)
label.pack(fill=tk.BOTH, expand=True)

# Привязываем обработчик нажатия клавиш к главному окну
root.bind("<KeyPress>", on_key_press)

# Запускаем обновление информационной карточки
# update_info_card()

# Запуск приложения
root.mainloop()
