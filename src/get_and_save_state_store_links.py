from os import path
from typing import List

from playwright.sync_api import Page, Playwright

from utils.proxies import ProxyManager
from utils.utils import (
    create_directory,
    get_output_path,
    get_page,
    get_url,
    navigate_to_page,
    run_playwright,
)

STORE_LINKS_QUERY = ".city-name a"
LOWES_STORES_URL = "https://www.lowes.com/Lowes-Stores"
STATES_STORES_LINKS_DIR = "states_stores_links"


def read_state_links() -> List[str]:
    print("Reading state links")
    with open(get_output_path("state_links.txt"), "r", encoding="utf-8") as file:
        state_links = file.readlines()
    return state_links


def get_store_links(page: Page) -> List[str]:
    store_link_els = page.query_selector_all(STORE_LINKS_QUERY)
    store_links = [el.get_attribute("href") for el in store_link_els]
    return store_links


def save_store_links(store_links: List[str], state: str) -> None:
    print(f"Saving store links for {state}")
    state_links_path = get_output_path(
        path.join(STATES_STORES_LINKS_DIR, f"{state}_store_links.txt")
    )
    with open(state_links_path, "w", encoding="utf-8") as file:
        for store_link in store_links:
            file.write(store_link + "\n")


def process_state_link(page: Page, state_link: str) -> None:
    state = state_link.split("/")[-2]
    print(f"Getting store links for {state}")

    navigate_to_page(page, get_url(state_link))
    store_links = get_store_links(page)
    save_store_links(store_links, state.lower())
    print(f"Done with {state}")


def runner(playwright: Playwright) -> None:
    print("Starting")

    create_directory(STATES_STORES_LINKS_DIR)
    state_links = read_state_links()

    if not state_links:
        print("No state links found, exiting")
        return

    proxy_manager = ProxyManager()

    try:
        for state_link in state_links:
            page = get_page(playwright, proxy_manager.get_next_proxy())
            process_state_link(page, state_link)
            page.close()

    except Exception as e:
        print(f"Error while processing the page - {e}")


def main():
    run_playwright(runner)


if __name__ == "__main__":
    main()
