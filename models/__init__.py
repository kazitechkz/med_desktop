import logging
import sys

from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Создаем базовый класс для моделей
Base = declarative_base()


def get_database_path():
    # Если приложение собрано с помощью PyInstaller
    if getattr(sys, 'frozen', False):
        # Путь к базе данных в скомпилированном приложении
        base_path = sys._MEIPASS
    else:
        # Путь для режима разработки
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, 'database.db')


# Путь к файлу базы данных SQLite
db_path = get_database_path()
engine = create_engine(f'sqlite:///{db_path}')
# Создаем сессию для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()


# Определение модели для типов телосложения
class BodyType(Base):
    __tablename__ = 'body_type'

    id = Column(Integer, primary_key=True)
    name = Column(Enum('asthenic', 'normosthenic', 'hypersthenic'), nullable=False)

    # Связь с таблицей reference_images
    reference_images = relationship('ReferenceImage', back_populates='body_type')


# Определение модели для эталонных изображений
class ReferenceImage(Base):
    __tablename__ = 'reference_images'

    id = Column(Integer, primary_key=True)
    body_type_id = Column(Integer, ForeignKey('body_type.id'), nullable=False)
    position = Column(Enum('PLAX', 'PSAX', 'A4C', 'A2C', 'A3C', 'subcostal', 'suprasternal'), nullable=False)
    image_path = Column(String(255), nullable=False)
    additional_image_path = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    body_type = relationship('BodyType', back_populates='reference_images')


# Добавление отношения "один-ко-многим" для body_type и reference_images
BodyType.reference_images = relationship('ReferenceImage', order_by=ReferenceImage.id, back_populates='body_type')

# Выполняем миграции для создания таблиц в базе данных, если их еще нет
Base.metadata.create_all(engine)
