import keyboard
import pyautogui
import pyperclip
import time
import webbrowser
import sys
import threading
import urllib.parse
import os
from PIL import Image, ImageDraw
import pystray

CLOUD_SERVER_URL = "http://localhost:8000" # frontend server URL

def run_sharp_search():
    try:
        time.sleep(0.05)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.15)

        keyword = pyperclip.paste().strip()
        if not keyword or len(keyword) > 50:
            return

        webbrowser.open(f"{CLOUD_SERVER_URL}/?q={urllib.parse.quote(keyword)}&t={int(time.time())}")

    except Exception as e:
        pass

def create_tray_icon(size=256):
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(image)
    
    padding = int(size * 0.0625) # 16
    d.ellipse([(padding, padding), (size - padding, size - padding)], fill=(254, 229, 0, 255))
    
    w = int(size * 0.0625) # 16
    pos1 = int(size * 0.406) # 104
    pos2 = int(size * 0.594) # 152
    start = int(size * 0.25) # 64
    end = int(size * 0.75)   # 192
    
    d.line([(start, pos1), (end, pos1)], fill=(25, 25, 25, 255), width=w)
    d.line([(start, pos2), (end, pos2)], fill=(25, 25, 25, 255), width=w)
    d.line([(pos1, start), (pos1, end)], fill=(25, 25, 25, 255), width=w)
    d.line([(pos2, start), (pos2, end)], fill=(25, 25, 25, 255), width=w)
    
    return image

def on_quit(icon, item):
    icon.stop()
    sys.exit(0)

def setup_tray():
    icon_image = create_tray_icon(64)
    menu = pystray.Menu(
        pystray.MenuItem('사용법: Ctrl + Alt + X', lambda: None, enabled=False),
        pystray.MenuItem('종료', on_quit)
    )
    icon = pystray.Icon("sharp_search", icon_image, "샵검색기", menu)
    icon.run()

if __name__ == "__main__":
    keyboard.add_hotkey('ctrl+alt+x', run_sharp_search)
    setup_tray()