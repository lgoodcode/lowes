from os import path
from typing import List

from playwright.sync_api import Page

from utils.utils import (create_directory, get_output_path, get_url,
                         navigate_to_page, runner)

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
    state_links_path = get_output_path(path.join(STATES_STORES_LINKS_DIR,f"{state}_store_links.txt"))
    with open(state_links_path, "w", encoding="utf-8") as file:
        for store_link in store_links:
            file.write(store_link + "\n")


def run(page: Page) -> None:
    print("Starting")

    create_directory(STATES_STORES_LINKS_DIR)
    state_links = read_state_links()

    if not state_links:
        print("No state links found, exiting")
        return

    # For each state link, get the store links
    for state_link in state_links:
        state = state_link.split("/")[-2]
        print(f"Getting store links for {state}")

        navigate_to_page(page, get_url(state_link))
        store_links = get_store_links(page)
        save_store_links(store_links, state.lower())
    print("Done!")


def main() -> None:
    runner(run)

if __name__ == "__main__":
    main()
