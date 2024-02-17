from os import path
from typing import Any, Dict

ROOT_DIR = path.dirname(path.abspath(__file__))
OUTPUT_DIR = path.join(ROOT_DIR, "output")

PROXIES_FILE_PATH = path.join(ROOT_DIR, "data", "proxies.txt")

CHROMIUM_KWARGS: Dict[str, Any] = {
    "headless": False,
    "channel": "chrome",
    "args": ["--disable-http2", "--no-sandbox"],
}


LOWES_URL = "https://www.lowes.com"
LOWES_STORES_URL = "https://www.lowes.com/Lowes-Stores"
