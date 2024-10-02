from PIL import Image, ImageDraw, ImageFont


def add_frame_mask(img, mask_path, active_position, alpha_value=0.5, scale_factor=0.5):
    """
    Накладывает маску и добавляет полосу с кнопками сверху, где активная позиция будет обёрнута зелёной рамкой.
    :param img: Исходное изображение
    :param mask_path: Путь к изображению маски
    :param active_position: Индекс активной позиции для выделения
    :param alpha_value: Значение прозрачности
    :param scale_factor: Коэффициент изменения размера маски
    :return: Изображение с наложенной маской и кнопками
    """
    # Загрузка маски
    mask_img = Image.open(mask_path).convert("RGBA")

    # Уменьшаем размер маски
    mask_width, mask_height = mask_img.size
    new_width = int(mask_width * scale_factor)
    new_height = int(mask_height * scale_factor)
    mask_img = mask_img.resize((new_width, new_height), Image.LANCZOS)

    # Изменяем прозрачность маски
    mask_img = reduce_transparency(mask_img, alpha_value)

    # Накладываем маску на изображение
    img_with_frame = img.convert("RGBA")
    img_width, img_height = img.size

    # Центрируем маску
    # position = ((img_width - new_width) // 2, (img_height - new_height) // 2)
    # img_with_frame.paste(mask_img, position, mask_img)

    # Центрируем маску по горизонтали и размещаем по верхнему краю по вертикали
    position = ((img_width - new_width) // 2, 50)  # '0' для верхнего края
    img_with_frame.paste(mask_img, position, mask_img)

    # Добавляем полупрозрачную маску в верхней части изображения и кнопки
    img_with_frame = add_privacy_mask_with_buttons(img_with_frame, active_position, height=50)

    return img_with_frame.convert("RGB")


def add_privacy_mask_with_buttons(img, active_position, height=50, color=(0, 0, 0, 128)):
    """
    Добавляет полупрозрачную маску с кнопками в верхней части изображения.
    Выделяет активную кнопку зелёной рамкой.
    :param img: Исходное изображение
    :param active_position: Индекс активной позиции для выделения
    :param height: Высота маски в пикселях
    :param color: Цвет маски в формате RGBA (по умолчанию полупрозрачный черный)
    :return: Изображение с наложенной маской и кнопками
    """
    draw = ImageDraw.Draw(img)
    # Накладываем полосу высотой height пикселей на верхнюю часть изображения
    draw.rectangle([0, 0, img.width, height], fill=color)

    # Подключаем шрифт, который поддерживает кириллицу
    try:
        font = ImageFont.truetype("arial.ttf", 14)  # Замените путь на реальный путь к файлу шрифта
    except IOError:
        font = ImageFont.load_default()

    # Добавляем кнопки для позиций
    positions = [
        'Парастернальная длинная ось (PLAX)',
        'Парастернальная короткая ось (PSAX)',
        'Апикальная четырехкамерная позиция (A4C)',
        'Апикальная двухкамерная позиция (A2C)',
        'Апикальная трехкамерная позиция (A3C)',
        'Субкостальная (подреберная) позиция',
        'Супрастернальная позиция'
    ]
    button_width = img.width // len(positions)
    button_height = height

    for i, position in enumerate(positions):
        # Определяем координаты для кнопки
        button_x1 = i * button_width
        button_x2 = button_x1 + button_width

        # Если кнопка активна, выделяем её зелёной рамкой
        if i == active_position:
            draw.rectangle([button_x1, 0, button_x2, button_height], outline="green", width=4)
        else:
            draw.rectangle([button_x1, 0, button_x2, button_height], outline="white", width=2)

        # Разбиваем текст на строки, чтобы он помещался в кнопку
        wrapped_text = wrap_text(position, font, button_width)

        # Рисуем текст построчно по центру кнопки
        text_y = 10  # Отступ сверху
        for line in wrapped_text:
            text_width, text_height = get_text_size(line,
                                                    font)  # Измеряем ширину и высоту текста с помощью get_text_size
            text_x = button_x1 + (button_width - text_width) // 2  # Центрируем текст по горизонтали
            draw.text((text_x, text_y), line, font=font, fill="white")
            text_y += text_height  # Смещаем Y для следующей строки

    return img


def wrap_text(text, font, max_width):
    """
    Разбивает текст на несколько строк, чтобы он помещался в указанную ширину.
    :param text: Текст для разбивки
    :param font: Шрифт для измерения длины текста
    :param max_width: Максимальная ширина строки в пикселях
    :return: Список строк, которые помещаются в указанную ширину
    """
    lines = []
    words = text.split(' ')
    current_line = []

    for word in words:
        # Проверяем, помещается ли текущая строка с добавленным словом
        test_line = ' '.join(current_line + [word])
        width, _ = get_text_size(test_line, font)
        if width <= max_width:
            current_line.append(word)
        else:
            # Строка уже не помещается, сохраняем её и начинаем новую
            lines.append(' '.join(current_line))
            current_line = [word]

    # Добавляем последнюю строку
    if current_line:
        lines.append(' '.join(current_line))

    return lines


def get_text_size(text, font):
    """
    Возвращает ширину и высоту текста с помощью метода getbbox для шрифта.
    :param text: Текст для измерения
    :param font: Шрифт, используемый для текста
    :return: Ширина и высота текста
    """
    bbox = font.getbbox(text)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


def reduce_transparency(img, alpha_value):
    """Изменяет прозрачность изображения."""
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda i: int(i * alpha_value))
    img = Image.merge('RGBA', (r, g, b, a))
    return img
