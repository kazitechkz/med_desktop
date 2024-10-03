# Методы для изменения позиции и размера
from tkinter import messagebox








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



