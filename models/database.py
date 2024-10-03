from models import session, BodyType, ReferenceImage
from models.seeds import seed_body_types, seed_reference_images  # Импорт сидов


class Database:
    def __init__(self):
        self.session = session

    def get_reference_images_by_body_type(self, body_type):
        """Возвращает все эталонные изображения для выбранного типа телосложения."""
        reference_images = (
            self.session.query(ReferenceImage)
            .join(BodyType)
            .filter(BodyType.name == body_type)
            .all()
        )
        return [(image.position, image.image_path, image.description) for image in reference_images]

    def is_database_empty(self):
        """Проверяет, есть ли записи в таблице ReferenceImage."""
        return self.session.query(ReferenceImage).first() is None

    def initialize_database(self):
        """Инициализация базы данных сидовыми данными, если она пуста."""
        if self.is_database_empty():
            print("Запуск сидов, так как база данных пуста...")
            seed_body_types(self.session)
            seed_reference_images(self.session)
            print("Сиды успешно загружены.")
        else:
            print("Данные в базе данных уже существуют.")
