import asyncio
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import ImageTk
from controllers.screen_controller import capture_screen
from controllers.frame_controller import add_frame_mask
from controllers.uploader import save_screenshot, upload_screenshot_async
from tkinter import ttk
from models.database import Database
from concurrent.futures import ThreadPoolExecutor


def get_body_type(text):
    if text == 'астеник':
        body_type = 'asthenic'
    elif text == 'нормостеник':
        body_type = 'normosthenic'
    else:
        body_type = 'hypersthenic'
    return body_type


class MainView:
    def __init__(self, root):
        self.root = root
        self.root.title("УЗИ с выбором каркаса и трансляцией")
        self.database = Database()
        # Устанавливаем окно в полный размер
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        # Инициализируем пул потоков
        self.executor = ThreadPoolExecutor(max_workers=2)

        # Обрабатываем нажатие клавиш
        self.root.bind("<KeyPress>", self.on_key_press)
        # Отключаем возможность изменения размера
        self.root.resizable(False, False)

        self.is_streaming = False  # Флаг для контроля состояния трансляции
        self.build_ui()

    def build_ui(self):
        # Добавим стиль для ttk
        # Фрейм для фильтров
        filter_frame = tk.Frame(self.root, bg='#f0f0f0')  # Добавим фоновый цвет
        filter_frame.pack(pady=20, padx=20, fill=tk.X)  # Расширим по оси X

        # Создаем Combobox для выбора типа телосложения
        self.body_type_var = tk.StringVar(value="астеник")
        body_type_combobox = ttk.Combobox(filter_frame, textvariable=self.body_type_var,
                                          values=["астеник", "нормостеник", "гиперстеник"], state="readonly")
        body_type_combobox.grid(row=0, column=0, padx=10, pady=5, sticky='w')  # Размещаем на первой позиции

        # Кнопка для начала трансляции, расположенная справа от Combobox
        start_button = ttk.Button(filter_frame, text="Начать трансляцию", command=self.start_stream, takefocus=False)
        start_button.grid(row=0, column=1, padx=10, pady=5, sticky='w')  # Размещаем на второй позиции в той же строке

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая часть экрана - информационная карточка с фиксированной шириной
        left_frame = tk.Frame(main_frame, width=300)  # Устанавливаем фиксированную ширину для левой части
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.info_label = tk.Label(left_frame, text="Загрузка данных с сервера", font=("Arial", 14), justify=tk.LEFT,
                                   anchor='w', wraplength=280)
        self.info_label.pack()

        self.preloader = ttk.Progressbar(left_frame, mode="indeterminate")
        self.preloader.pack(pady=10)
        self.preloader.pack_forget()

        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.label = tk.Label(self.right_frame)
        self.label.pack(fill=tk.BOTH, expand=True)

    def start_stream(self):
        if self.is_streaming:
            self.is_streaming = False
            self.root.after_cancel(self.stream_job)  # Остановка таймера при остановке стрима
            return

        # Получаем выбранный тип телосложения
        body_type_var = self.body_type_var.get()
        body_type = get_body_type(body_type_var)
        print(body_type)
        # Загружаем эталонные изображения для выбранного типа телосложения
        reference_images = self.database.get_reference_images_by_body_type(body_type)

        if not reference_images:
            messagebox.showerror("Ошибка", "Нет эталонных изображений для выбранного типа телосложения.")
            return

        self.reference_images = reference_images  # Сохраняем список эталонных изображений
        self.current_position_index = 0  # Начнем с первой позиции

        self.is_streaming = True
        self.update_image()  # Начинаем трансляцию

    def update_image(self):
        self.update_mask()

        # Устанавливаем таймер для следующего обновления
        self.stream_job = self.root.after(50, self.update_image)

    def on_key_press(self, event):
        if event.char.isdigit():  # Проверяем, что символ - цифра
            index = int(event.char) - 1  # Преобразуем символ в число и используем его как индекс
            if 0 <= index < len(self.reference_images):  # Убеждаемся, что индекс в пределах доступных позиций
                self.current_position_index = index
                # Не перезапускаем таймер, а просто обновляем маску
                self.update_mask()
        if event.keysym == "space":
            self.save_and_upload_screenshot()

    def save_and_upload_screenshot(self):
        """Захват скриншота и отправка на сервер."""
        img = capture_screen()
        file_path = save_screenshot(img)

        # Показываем прелоадер
        self.preloader.pack(pady=10)
        self.info_label.config(text="Отправка скриншота на сервер...")
        self.info_label.pack()

        # Запускаем асинхронную загрузку
        async def upload():
            result = await upload_screenshot_async(file_path)
            self.root.after(0, self.upload_complete, result)

        asyncio.run(upload())  # Запускаем асинхронную загрузку

    def upload_complete(self, result):
        """Обновление интерфейса после загрузки."""
        self.preloader.pack_forget()
        self.info_label.config(text=f"Результат: {result}", fg="green")

    def load_reference_images(self):
        """Загружает эталонные изображения для выбранного типа телосложения."""
        body_type_var = self.body_type_var.get()
        body_type = get_body_type(body_type_var)
        # Загружаем эталонные изображения для выбранного типа телосложения
        reference_images = self.database.get_reference_images_by_body_type(body_type)

        if not reference_images:
            messagebox.showerror("Ошибка", "Нет эталонных изображений для выбранного типа телосложения.")
            return

        self.reference_images = reference_images  # Сохраняем список эталонных изображений
        self.current_position_index = 0  # Устанавливаем первую позицию по умолчанию

    def update_mask(self):
        """Обновляет только маску, не перезапуская весь стрим."""
        if not self.is_streaming:
            return

        # Захватываем текущее изображение
        img = capture_screen()

        # Получаем размеры второго монитора и масштабируем изображение
        monitor_width, monitor_height = img.size
        frame_width = self.right_frame.winfo_width()
        frame_height = self.right_frame.winfo_height()
        scale = min(frame_width / monitor_width, frame_height / monitor_height)

        new_width = int(monitor_width * scale)
        new_height = int(monitor_height * scale)
        img_resized = img.resize((new_width, new_height))

        # Получаем текущую маску для позиции
        current_position, mask_path = self.reference_images[self.current_position_index]

        # Накладываем маску на изображение
        img_with_frame = add_frame_mask(img_resized, mask_path, self.current_position_index)

        # Конвертируем изображение для отображения в tkinter
        img_tk = ImageTk.PhotoImage(img_with_frame)
        self.label.config(image=img_tk)
        self.label.image = img_tk
