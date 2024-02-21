import random
from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

from lowes.utils.logger import get_logger

load_dotenv()

logger = get_logger()

PROXY_URL = "http://customer-%s-sessid-%s:%s@pr.oxylabs.io:7777"
HEXT_DIGITS = "0123456789ABCDEF"


def generate_hex_id(length: int = 6) -> str:
    id_str = ""
    for _ in range(length):
        id_str += random.choice(HEXT_DIGITS)
    return id_str


@dataclass
class Proxy:
    server: str
    username: str
    password: str

    def __init__(self):
        user = getenv("PROXY_USER")
        password = getenv("PROXY_PASS")

        if not user or not password:
            raise Exception("Proxy not set")

        self.server = PROXY_URL % (user, generate_hex_id(), password)
        self.username = user
        self.password = password
