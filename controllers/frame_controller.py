from PIL import Image, ImageDraw


def add_frame_mask(img, mask_path, alpha_value=0.5):
    # Загрузка маски
    mask_img = Image.open(mask_path).convert("RGBA")

    # Изменяем прозрачность маски
    mask_img = reduce_transparency(mask_img, alpha_value)

    # Накладываем маску на изображение
    img_with_frame = img.convert("RGBA")
    img_width, img_height = img.size
    mask_width, mask_height = mask_img.size
    position = ((img_width - mask_width) // 2, (img_height - mask_height) // 2)
    img_with_frame.paste(mask_img, position, mask_img)

    # Добавляем полупрозрачную маску в верхней части изображения
    img_with_frame = add_privacy_mask(img_with_frame, height=100)

    return img_with_frame.convert("RGB")


def add_privacy_mask(img, height=100, color=(0, 0, 0, 128)):
    """
    Добавляет полупрозрачную маску в верхней части изображения.
    :param img: Исходное изображение
    :param height: Высота маски в пикселях
    :param color: Цвет маски в формате RGBA (по умолчанию полупрозрачный черный)
    :return: Изображение с наложенной маской
    """
    draw = ImageDraw.Draw(img)
    # Накладываем полосу высотой height пикселей на верхнюю часть изображения
    draw.rectangle([0, 0, img.width, height], fill=color)
    return img


def reduce_transparency(img, alpha_value):
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda i: int(i * alpha_value))
    img = Image.merge('RGBA', (r, g, b, a))
    return img
