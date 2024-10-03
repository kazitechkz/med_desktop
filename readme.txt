pyinstaller --onefile --add-data "models/database.db;models" --add-data "assets;masks" --hidden-import "sqlalchemy.dialects.sqlite" --name medapp --noconsole app.py
