from models import session, BodyType, ReferenceImage


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
        return [(image.position, image.image_path) for image in reference_images]
