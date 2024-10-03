import asyncio
import os
import threading
from datetime import datetime
from random import randint

import requests

from controllers.screen_controller import capture_screen


def save_screenshot(img):
    """Сохраняем скриншот."""
    if not os.path.exists("assets/screenshots"):
        os.makedirs("assets/screenshots")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"assets/screenshots/screenshot_{timestamp}.png"
    img.save(file_path)
    return file_path


async def upload_screenshot_async(file_path):
    return f"{randint(50, 100)} %"
    # """Асинхронная загрузка скриншота на сервер."""
    # url = 'http://localhost:5000/upload'
    # try:
    #     async with aiohttp.ClientSession() as session:
    #         with open(file_path, 'rb') as f:
    #             files = {'file': f}
    #             async with session.post(url, data=files) as response:
    #                 return await response.text()
    # except Exception as e:
    #     print(f"Ошибка при отправке: {e}")
    #     return False


def upload_screenshot_sync(file_path):
    """Синхронная загрузка (резервный вариант)."""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:5000/upload', files=files)
            return response.text
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
        return False



