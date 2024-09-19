import mss
from PIL import Image


def capture_screen(monitor_index=2):
    with mss.mss() as sct:
        screen = sct.grab(sct.monitors[monitor_index])  # Захват экрана второго монитора
        img = Image.frombytes("RGB", (screen.width, screen.height), screen.rgb)
        return img
