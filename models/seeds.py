from models import session, BodyType, ReferenceImage


def seed_body_types():
    """Заполняем таблицу body_type начальными данными"""
    body_types = [
        BodyType(name='asthenic'),
        BodyType(name='normosthenic'),
        BodyType(name='hypersthenic')
    ]

    session.add_all(body_types)
    session.commit()
    print("Таблица body_type заполнена данными.")


def seed_reference_images():
    """Заполняем таблицу reference_images начальными данными"""

    # Получаем записи из таблицы body_type
    body_types = session.query(BodyType).all()

    # Для каждого типа телосложения добавляем изображения для каждой позиции
    reference_images = []

    for body_type in body_types:
        positions = ['PLAX', 'PSAX', 'A4C', 'A2C', 'A3C', 'subcostal', 'suprasternal']
        for position in positions:
            image_path = f'assets/masks/{body_type.name.lower()}_{position.lower()}.png'
            reference_images.append(
                ReferenceImage(body_type_id=body_type.id, position=position, image_path=image_path)
            )

    session.add_all(reference_images)
    session.commit()
    print("Таблица reference_images заполнена данными.")


if __name__ == '__main__':
    seed_body_types()
    seed_reference_images()
    print("Сиды успешно созданы.")
