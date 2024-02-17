from dataclasses import dataclass
from os import path

from constants import PROXIES_FILE, ROOT_DIR


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


def read_proxy_list() -> list[str]:
    print(
        "Reading proxy listReading proxy listReading proxy listReading proxy listReading proxy listReading proxy listReading proxy list"
    )
    with open(path.join(ROOT_DIR, PROXIES_FILE), "r", encoding="utf-8") as file:
        proxies = file.readlines()
    return proxies


@dataclass
class ProxyManager:
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

    def set_proxy_inactive(self, server: str) -> None:
        """Marks a proxy as inactive based on its address."""
        for _, proxy in enumerate(self.proxy_list):
            if proxy.server == server:
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
