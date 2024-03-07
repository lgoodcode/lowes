from os import path
from typing import Any, Dict

ROOT_DIR = path.dirname(path.abspath(__file__))
OUTPUT_DIR = path.join(ROOT_DIR, "output")

PROXIES_FILE_PATH = path.join(ROOT_DIR, "data", "proxies.txt")

CHROMIUM_KWARGS: Dict[str, Any] = {
    "channel": "chrome",
    "args": ["--disable-http2", "--no-sandbox"],
}


LOWES_URL = "https://www.lowes.com"
LOWES_STORES_URL = "https://www.lowes.com/Lowes-Stores"
LOWES_DEPARTMENTS_URL = "https://www.lowes.com/c/Departments"

DEPARTMENT_LINKS_PATH = path.join(OUTPUT_DIR, "department_links.txt")
STATE_STORE_LINKS_PATH = path.join(OUTPUT_DIR, "state_links.txt")
STATE_STORES_LINKS_DIR = path.join(OUTPUT_DIR, "stores_links")
STATE_STORE_INFO_DIR = path.join(OUTPUT_DIR, "store_infos")
