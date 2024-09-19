import requests
import os
from datetime import datetime


def save_screenshot(img):
    if not os.path.exists("assets/screenshots"):
        os.makedirs("assets/screenshots")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"assets/screenshots/screenshot_{timestamp}.png"
    img.save(file_path)
    return file_path


def upload_screenshot(file_path):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:5000/upload', files=files)
            return response.text
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
        return False
