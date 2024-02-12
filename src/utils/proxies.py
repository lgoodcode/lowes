from dataclasses import dataclass
from os import path

from playwright.sync_api import ProxySettings

from constants import ROOT_DIR

PROXIES_FILE = "proxies.txt"


@dataclass
class Proxy:
    """Represents a proxy server."""

    def __init__(self, proxy: str):
        proxy = proxy.strip()
        parts = proxy.split(":")
        self.server = parts[0] + ":" + parts[1]
        self.username = parts[2]
        self.password = parts[3]


def read_proxy_list() -> list[str]:
    print("Reading proxy list")
    with open(path.join(ROOT_DIR, PROXIES_FILE), "r", encoding="utf-8") as file:
        proxies = file.readlines()
    return proxies


def create_playwright_proxy_settings(proxy: Proxy) -> ProxySettings:
    return ProxySettings(
        server=proxy.server,
        username=proxy.username,
        password=proxy.password,
    )


@dataclass
class ProxyManager:
    """Manages a list of proxies and provides methods to get active proxies.

    Raises:
        ValueError: If no active proxies are available.

    Returns:
        _type_: ProxyManager
    """

    proxy_list: list[Proxy]
    current_index: int = 0

    def __init__(self):
        proxies = read_proxy_list()
        self.proxy_list = [Proxy(proxy) for proxy in proxies]

    def get_active_proxy(self) -> Proxy:
        """Returns a currently active proxy from the list."""
        while not self.proxy_list[self.current_index].active:
            self.current_index = (self.current_index + 1) % len(self.proxy_list)
        return self.proxy_list[self.current_index]

    def set_proxy_inactive(self, address: str):
        """Marks a proxy as inactive based on its address."""
        for _, proxy in enumerate(self.proxy_list):
            if proxy.address == address:
                proxy.active = False
                self.current_index = (self.current_index - 1) % len(self.proxy_list)
                break

    def get_next_proxy(self) -> Proxy:
        """Returns the next proxy in the list."""
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        return self.proxy_list[self.current_index]

    # def random_active_proxy(self) -> Proxy:
    #     """Returns a random active proxy from the list."""
    #     count = 0
    #     active_proxies = [proxy for proxy in self.proxy_list if proxy.active]
    #     while count < len(active_proxies):
    #         index = randrange(len(active_proxies))
    #         proxy = active_proxies[index]
    #         if proxy.active:
    #             return proxy
    #         count += 1
    #     raise ValueError("No active proxies available")
