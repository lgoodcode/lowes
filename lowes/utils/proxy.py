from dataclasses import dataclass
from typing import Any

from lowes.constants import PROXIES_FILE_PATH
from lowes.utils.logger import get_logger

logger = get_logger()


class Singleton(object):
    _instance = None

    def __new__(cls, *args: Any, **kwargs: Any):
        """
        Ensures only one instance of the class is created.

        Args:
            *args: Arguments passed to the class constructor.
            **kwargs: Keyword arguments passed to the class constructor.

        Returns:
            The instance of the class.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Prevents further initialization after the first instance is created.

        Args:
            *args: Arguments passed to the class constructor.
            **kwargs: Keyword arguments passed to the class constructor.
        """
        if self.__class__._instance is not self:
            raise RuntimeError("Call __init__ only once!")


def read_proxy_list() -> list[str]:
    logger.info("Reading proxy list")

    with open(PROXIES_FILE_PATH, "r", encoding="utf-8") as file:
        proxies = file.readlines()
    return proxies


@dataclass
class Proxy:
    server: str
    username: str
    password: str
    active: bool = False

    def __init__(self, proxies: str):
        proxies = proxies.strip()
        ip, port, username, password = proxies.split(":")
        self.server = ip + ":" + port
        self.username = username
        self.password = password


@dataclass
class ProxyManager(Singleton):
    proxy_list: list[Proxy]
    instantiated: bool = False
    current_index: int = 0

    def __init__(self):
        if self.instantiated:
            return

        proxies = read_proxy_list()
        self.proxy_list = [Proxy(proxy) for proxy in proxies]
        self.instantiated = True

    def get_next_proxy(self) -> Proxy:
        """Returns the next proxy in the list."""
        current_proxy = self.proxy_list[self.current_index]
        current_proxy.active = False

        self.current_index = (self.current_index + 1) % len(self.proxy_list)

        next_proxy = self.proxy_list[self.current_index]
        next_proxy.active = True

        logger.info(f"[Proxy] {next_proxy.server}")
        return next_proxy
