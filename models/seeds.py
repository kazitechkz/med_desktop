from models import session, BodyType, ReferenceImage


def seed_body_types(session):
    """Заполняем таблицу body_type начальными данными"""
    body_types = [
        BodyType(name='asthenic'),
        BodyType(name='normosthenic'),
        BodyType(name='hypersthenic')
    ]

    session.add_all(body_types)
    session.commit()
    print("Таблица body_type заполнена данными.")


def seed_reference_images(session):
    """Заполняем таблицу reference_images начальными данными"""

    # Получаем записи из таблицы body_type
    body_types = session.query(BodyType).all()

    # Для каждого типа телосложения добавляем изображения для каждой позиции
    reference_images = []

    for body_type in body_types:
        positions = ['PLAX', 'PSAX', 'A4C', 'A2C', 'A3C', 'subcostal', 'suprasternal']
        for position in positions:
            image_path = f'assets/masks/{body_type.name.lower()}_{position.lower()}.png'

            # Добавляем описание для позиции PLAX
            if position == 'PLAX':
                description = """
                А – метка датчика, условно стоит всегда в центре поля сканирования и все координаты ведутся от нее.
                В – место контакта синуса Вальсальвы аорты и межжелудочковой перегородки, т. н. аортально-септальный контакт,
                при верном выведении продольной парастернальной позиции по длинной оси (PLAX) находится примерно в центре поля
                сканирования под точкой А (меткой датчика).
                Дистанции В-С (по межжелудочковой перегородке) и В-D (по корню аорты) при правильном выведении PLAX примерно равны.
                При правильном выведении обязательно видим весь корень аорты и не менее такой же части восходящей проксимальной
                аорты (дистанции E и F).
                При правильном выведении область митрального клапана почти посередине и под точкой А внизу поля сканирования.
                Должны визуализироваться 2/3 левого желудочка (дистанция Н) и не должна быть видна его верхушка (дистанция I).
                Длинная ось левого желудочка (линия 1) должна быть как можно более горизонтальной, т. е. левый желудочек должен 
                «лежать» вдоль нижней части экрана. При этом между длинной осью левого желудочка (линия 1) и направлением луча 
                датчика (линия 2) на уровне кончиков раскрытых створок митрального клапана должен быть угол 90° (точка 3).
                """
            else:
                description = None

            reference_images.append(
                ReferenceImage(
                    body_type_id=body_type.id,
                    position=position,
                    image_path=image_path,
                    description=description
                )
            )

    session.add_all(reference_images)
    session.commit()
    print("Таблица reference_images заполнена данными.")


if __name__ == '__main__':
    seed_body_types()
    seed_reference_images()
    print("Сиды успешно созданы.")
