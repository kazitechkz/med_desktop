import asyncio
import logging
import threading
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox
from tkinter import ttk

from PIL import Image, ImageTk

from controllers.frame_controller import add_frame_mask
from controllers.screen_controller import capture_screen
from controllers.uploader import upload_screenshot_async, save_screenshot
from models.database import Database


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
        self.right_frame = None
        # self.left_frame = None
        self.description_label = None
        self.root = root
        self.root.title("УЗИ с выбором каркаса и трансляцией")
        self.database = Database()
        # Устанавливаем окно в полный размер
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        # Инициализируем пул потоков
        self.executor = ThreadPoolExecutor(max_workers=2)
        # Инициализируем параметры для управления положением и размером
        self.mask_position_x = 150  # Позиция по X
        self.mask_position_y = 50  # Позиция по Y
        self.scale_factor = 0.7  # Масштаб маски
        # Обрабатываем нажатие клавиш
        self.root.bind("<KeyPress>", self.on_key_press)
        # Отключаем возможность изменения размера
        self.root.resizable(False, False)

        self.is_streaming = False  # Флаг для контроля состояния трансляции
        self.build_ui()

    def build_ui(self):
        # Фрейм для фильтров и управления
        filter_frame = tk.Frame(self.root, bg='#f0f0f0', height=150)  # Ограничим высоту
        filter_frame.pack(pady=20, padx=20, fill=tk.X)

        # Создаем Combobox для выбора типа телосложения
        self.body_type_var = tk.StringVar(value="астеник")
        body_type_combobox = ttk.Combobox(filter_frame, textvariable=self.body_type_var,
                                          values=["астеник", "нормостеник", "гиперстеник"], state="readonly", width=15)
        body_type_combobox.pack(side=tk.LEFT, padx=10, pady=5)

        # Кнопка для начала трансляции
        start_button = ttk.Button(filter_frame, text="Начать трансляцию", command=self.start_stream, takefocus=False)
        start_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Фрейм для кнопок управления положением и размером
        control_frame = tk.Frame(filter_frame)
        control_frame.pack(side=tk.LEFT, padx=10, pady=5)

        # Кнопки для управления положением по Y
        tk.Label(control_frame, text="Y:", width=5).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="▲", command=self.increase_y, width=2).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="▼", command=self.decrease_y, width=2).pack(side=tk.LEFT, padx=2)

        # Кнопки для управления положением по X
        tk.Label(control_frame, text="X:", width=5).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="◄", command=self.decrease_x, width=2).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="►", command=self.increase_x, width=2).pack(side=tk.LEFT, padx=2)

        # Кнопки для управления размером
        tk.Label(control_frame, text="Размер:", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="+", command=self.increase_size, width=2).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="-", command=self.decrease_size, width=2).pack(side=tk.LEFT, padx=2)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая часть экрана - информационная карточка с фиксированной шириной
        self.left_frame = tk.Frame(main_frame, width=300,
                                   bg="lightgray")  # Устанавливаем фиксированную ширину для левой части
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        # Отключаем возможность изменения размера фрейма в зависимости от содержимого
        self.left_frame.pack_propagate(False)

        self.info_label = tk.Label(self.left_frame, text="Загрузка данных с сервера", font=("Arial", 14),
                                   justify=tk.LEFT, anchor='w', wraplength=280)
        self.info_label.pack(pady=10)

        # Лейбл для отображения дополнительного изображения
        self.additional_image_label = tk.Label(self.left_frame)
        self.additional_image_label.pack(pady=10)

        # Добавляем фрейм для текстового поля с описанием и скролла
        self.text_frame = tk.Frame(self.left_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Добавляем скроллбар
        self.text_scroll = tk.Scrollbar(self.text_frame)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Текстовое поле для описания с прокруткой
        self.description_text = tk.Text(self.text_frame, wrap=tk.WORD, yscrollcommand=self.text_scroll.set, height=5)
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Привязываем скроллбар к текстовому полю
        self.text_scroll.config(command=self.description_text.yview)

        # Изначально скрываем текстовое поле
        self.text_frame.pack_forget()

        # Кнопка для скрытия/показа текста
        self.toggle_button = ttk.Button(self.left_frame, text="Показать описание", command=self.toggle_description,
                                        takefocus=False)
        self.toggle_button.pack(pady=5)

        self.preloader = ttk.Progressbar(self.left_frame, mode="indeterminate")
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

        # Загружаем эталонные изображения для выбранного типа телосложения
        reference_images = self.database.get_reference_images_by_body_type(body_type)
        if not reference_images:
            messagebox.showerror("Ошибка", "Нет эталонных изображений для выбранного типа телосложения.")
            return

        self.reference_images = reference_images  # Сохраняем список эталонных изображений
        self.current_position_index = 0  # Начнем с первой позиции

        self.is_streaming = True
        self.update_image()  # Начинаем трансляцию

    def on_key_press(self, event):
        if event.char.isdigit():  # Проверяем, что символ - цифра
            index = int(event.char) - 1  # Преобразуем символ в число и используем его как индекс
            if 0 <= index < len(self.reference_images):  # Убеждаемся, что индекс в пределах доступных позиций
                self.current_position_index = index
                # Не перезапускаем таймер, а просто обновляем маску
                self.update_mask()
        if event.keysym == "space":
            self.save_and_upload_screenshot()

        # Управление положением по X и Y
        if event.keysym == "Up":  # Стрелка вверх
            self.increase_y()
        elif event.keysym == "Down":  # Стрелка вниз
            self.decrease_y()
        elif event.keysym == "Left":  # Стрелка влево
            self.decrease_x()
        elif event.keysym == "Right":  # Стрелка вправо
            self.increase_x()

        # Управление размером
        if event.keysym == "plus" or event.keysym == "KP_Add":  # Клавиша "+" (на основной клавиатуре и на цифровой)
            self.increase_size()
        elif event.keysym == "minus" or event.keysym == "KP_Subtract":  # Клавиша "-" (на основной клавиатуре и на цифровой)
            self.decrease_size()

    def update_description(self, description):
        # Если описание найдено, обновляем текст в description_label
        if description:
            self.description_label.config(text=description)
        else:
            self.description_label.config(text="Описание для данной позиции отсутствует.")

    def update_image(self):
        self.update_mask()

        # Устанавливаем таймер для следующего обновления
        self.stream_job = self.root.after(50, self.update_image)

    def upload_complete(self, result):
        """Обновление интерфейса после загрузки."""
        self.preloader.pack_forget()
        self.info_label.config(text=f"Результат: {result}", fg="green")

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
        current_position, mask_path, description, additional_image_path = self.reference_images[
            self.current_position_index]

        img_with_frame = add_frame_mask(img_resized, mask_path, self.current_position_index,
                                        scale_factor=self.scale_factor, pos_x=self.mask_position_x,
                                        pos_y=self.mask_position_y)

        # Конвертируем изображение для отображения в tkinter
        img_tk = ImageTk.PhotoImage(img_with_frame)
        self.label.config(image=img_tk)
        self.label.image = img_tk

        # Обновляем описание для текущей позиции
        self.update_additional_image(additional_image_path)
        self.current_description = description

    def update_additional_image(self, additional_image_path):
        """Загружает и отображает дополнительное изображение."""
        if additional_image_path:
            additional_img = Image.open(additional_image_path)
            additional_img_resized = additional_img.resize((280, 500))  # Изменяем размер изображения
            additional_img_tk = ImageTk.PhotoImage(additional_img_resized)
            self.additional_image_label.config(image=additional_img_tk)
            self.additional_image_label.image = additional_img_tk
        else:
            self.additional_image_label.config(image=None)
            self.additional_image_label.image = None

    def toggle_description(self):
        """Скрывает или показывает текст описания."""
        if self.text_frame.winfo_ismapped():  # Проверяем, отображается ли текст
            self.text_frame.pack_forget()  # Скрываем текст
            self.toggle_button.config(text="Показать описание")
        else:
            self.text_frame.pack(fill=tk.BOTH, expand=True)  # Показываем текст
            self.toggle_button.config(text="Скрыть описание")
            self.show_description()

    def show_description(self):
        """Обновляет текст в виджете Text."""
        self.description_text.delete(1.0, tk.END)  # Очищаем текстовое поле
        if self.current_description:
            self.description_text.insert(tk.END, self.current_description)  # Вставляем новое описание
        else:
            self.description_text.insert(tk.END, "Описание недоступно.")

    def save_and_upload_screenshot(self):
        """Захват скриншота и отправка на сервер."""
        img = capture_screen()
        file_path = save_screenshot(img)

        # Показываем прелоадер
        self.preloader.pack(pady=10)
        self.info_label.config(text="Отправка скриншота на сервер...")
        self.info_label.pack()

        # Запускаем загрузку в отдельном потоке, чтобы не блокировать интерфейс
        threading.Thread(target=self.upload_screenshot_thread, args=(file_path,)).start()

    def upload_screenshot_thread(self, file_path):
        """Асинхронная загрузка скриншота в отдельном потоке."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Выполняем асинхронную функцию
        result = loop.run_until_complete(upload_screenshot_async(file_path))

        # Возвращаемся в главный поток Tkinter для обновления интерфейса
        self.root.after(0, self.upload_complete, result)

    def increase_y(self):
        self.mask_position_y -= 10  # Двигаем маску вверх
        self.update_mask()

    def decrease_y(self):
        self.mask_position_y += 10  # Двигаем маску вниз
        self.update_mask()

    def increase_x(self):
        self.mask_position_x += 10  # Двигаем маску вправо
        self.update_mask()

    def decrease_x(self):
        self.mask_position_x -= 10  # Двигаем маску влево
        self.update_mask()

    def increase_size(self):
        self.scale_factor += 0.1  # Увеличиваем масштаб
        self.update_mask()

    def decrease_size(self):
        self.scale_factor = max(0.1, self.scale_factor - 0.1)  # Уменьшаем масштаб, но не меньше 0.1
        self.update_mask()
