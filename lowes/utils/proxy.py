from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()

PROXY_URL = "http://customer-%s:%s@pr.oxylabs.io:7777"


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

        # self.server = PROXY_URL % (user, password)
        # self.username = user
        # self.password = password
        self.server = "216.185.62.133:3486"
        self.username = "ssfogbsa"
        self.password = "jrscgC07HA"
