import tkinter as tk
from tkinter import messagebox, ttk
from PIL import ImageTk
import threading
from controllers.screen_controller import capture_screen
from controllers.frame_controller import add_frame_mask
from controllers.uploader import save_screenshot, upload_screenshot
from tkinter import ttk


class MainView:
    def __init__(self, root):
        self.root = root
        self.root.title("УЗИ с выбором каркаса и трансляцией")

        # Устанавливаем окно в полный размер
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")

        # Отключаем возможность изменения размера
        self.root.resizable(False, False)

        self.is_streaming = False  # Флаг для контроля состояния трансляции
        self.build_ui()

    def build_ui(self):
        # Добавим стиль для ttk
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12), padding=10)
        style.configure('TButton', font=('Arial', 12), padding=10)
        style.configure('TCombobox', font=('Arial', 12), padding=5)

        # Фрейм для фильтров
        filter_frame = tk.Frame(self.root, bg='#f0f0f0')  # Добавим фоновый цвет
        filter_frame.pack(pady=20, padx=20)

        self.gender_var = tk.StringVar(value="Мужчина")
        self.body_type_var = tk.StringVar(value="Худой")
        self.height_var = tk.StringVar(value="Высокий")

        # Пол
        ttk.Label(filter_frame, text="Пол:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        gender_combobox = ttk.Combobox(filter_frame, textvariable=self.gender_var, values=["Мужчина", "Женщина"],
                                       state="readonly")
        gender_combobox.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        # Тип телосложения
        ttk.Label(filter_frame, text="Тип телосложения:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        body_type_combobox = ttk.Combobox(filter_frame, textvariable=self.body_type_var, values=["Худой", "Толстый"],
                                          state="readonly")
        body_type_combobox.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        # Рост
        ttk.Label(filter_frame, text="Рост:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        height_combobox = ttk.Combobox(filter_frame, textvariable=self.height_var, values=["Высокий", "Низкий"],
                                       state="readonly")
        height_combobox.grid(row=2, column=1, padx=10, pady=5, sticky='w')

        # Кнопка для начала трансляции
        start_button = ttk.Button(filter_frame, text="Начать трансляцию", command=self.start_stream)
        start_button.grid(row=3, column=0, columnspan=2, pady=20)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая часть экрана - информационная карточка с фиксированной шириной
        left_frame = tk.Frame(main_frame, width=300)  # Устанавливаем фиксированную ширину для левой части
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.info_label = tk.Label(left_frame, text="Загрузка данных с сервера", font=("Arial", 14), justify=tk.LEFT, anchor='w', wraplength=280)
        self.info_label.pack()

        self.preloader = ttk.Progressbar(left_frame, mode="indeterminate")
        self.preloader.pack(pady=10)
        self.preloader.pack_forget()

        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.label = tk.Label(self.right_frame)
        self.label.pack(fill=tk.BOTH, expand=True)

        self.root.bind("<KeyPress>", self.on_key_press)

    def start_stream(self):
        if self.is_streaming:
            self.is_streaming = False
            self.root.after_cancel(self.stream_job)

        mask_path = self.get_frame_path()
        if not mask_path:
            messagebox.showerror("Ошибка", f"Файл маски не найден: {mask_path}")
            return

        self.is_streaming = True
        self.update_image(mask_path)

    def update_image(self, mask_path):
        if not self.is_streaming:
            return

        # Захватываем изображение с второго монитора
        img = capture_screen()

        # Получаем размеры второго монитора
        monitor_width, monitor_height = img.size

        # Получаем размеры правой части экрана, куда будем выводить трансляцию
        frame_width = self.right_frame.winfo_width()
        frame_height = self.right_frame.winfo_height()

        # Вычисляем масштаб, чтобы сохранить соотношение сторон
        scale = min(frame_width / monitor_width, frame_height / monitor_height)

        # Изменяем размер изображения с учетом масштаба
        new_width = int(monitor_width * scale)
        new_height = int(monitor_height * scale)
        img_resized = img.resize((new_width, new_height))

        # Накладываем маску на изображение
        img_with_frame = add_frame_mask(img_resized, mask_path)

        # Конвертируем изображение для отображения в tkinter
        img_tk = ImageTk.PhotoImage(img_with_frame)
        self.label.config(image=img_tk)
        self.label.image = img_tk

        # Устанавливаем таймер для следующего обновления
        self.stream_job = self.root.after(50, self.update_image, mask_path)

    def on_key_press(self, event):
        if event.keysym == "space":
            self.save_and_upload_screenshot()

    def save_and_upload_screenshot(self):
        img = capture_screen()
        file_path = save_screenshot(img)

        self.preloader.pack(pady=10)
        self.info_label.config(text="Отправка скриншота на сервер...")

        def upload_thread():
            result = upload_screenshot(file_path)
            self.preloader.pack_forget()
            self.info_label.config(text=f"{result}", fg="green")

        threading.Thread(target=upload_thread).start()

    def get_frame_path(self):
        gender = self.gender_var.get()
        body_type = self.body_type_var.get()
        height = self.height_var.get()

        if gender == "Мужчина" and body_type == "Худой" and height == "Высокий":
            return "assets/masks/mask_male_thin_tall.png"
        elif gender == "Женщина" and body_type == "Толстый" and height == "Низкий":
            return "assets/masks/mask_female_fat_short.jpg"
        return "assets/masks/mask_female_fat_short.jpg"
