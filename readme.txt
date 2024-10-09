pyinstaller --onefile --add-data "models/database.db;models" --add-data "assets;masks" --add-data "assets;additional_images" --hidden-import "sqlalchemy.dialects.sqlite" --name med --noconsole app.py
