from os import path

from playwright.sync_api import Page, Playwright

from lowes.utils.playwright import get_el, get_page, navigate_to_page
from lowes.utils.proxies import ProxyManager
from lowes.utils.utils import create_directory, get_full_lowes_url, get_output_path

LOWES_STORES_URL = "https://www.lowes.com/Lowes-Stores"
STATES_STORES_LINKS_DIR = "states_stores_links"
STATES_STORES_IDS_DIR = "states_stores_ids"
STORE_LINKS_SELECTOR = ".city-name a"
STORE_ID_SELECTOR = "span.storeNo"


def get_store_id(page: Page) -> str:
    store_id_el = get_el(page, STORE_ID_SELECTOR)
    raw_store_id_text = store_id_el.inner_text()
    store_id = raw_store_id_text.split("#")[1]
    return store_id


def read_state_links() -> list[str]:
    print("Reading state links")
    with open(get_output_path("state_links.txt"), "r", encoding="utf-8") as file:
        state_links = file.readlines()
    return state_links


def get_store_links(page: Page) -> list[str]:
    store_link_els = page.query_selector_all(STORE_LINKS_SELECTOR)
    store_links: list[str] = []

    for store_link in store_link_els:
        if href := store_link.get_attribute("href"):
            store_links.append(href)
    return store_links


def get_state_store_links(page: Page, state_link: str, state: str) -> list[str]:
    """Navigate to list of all stores in the state, get all the store links,
    save them to a file, and return them."""

    navigate_to_page(page, get_full_lowes_url(state_link))
    store_links = get_store_links(page)
    save_store_links(store_links, state)
    return store_links


def save_store_links(store_links: list[str], state: str) -> None:
    print(f"[{state}] - Saving store links")

    create_directory(STATES_STORES_LINKS_DIR)
    state_links_path = get_output_path(
        path.join(STATES_STORES_LINKS_DIR, f"{state.lower()}_store_links.txt")
    )
    with open(state_links_path, "w", encoding="utf-8") as file:
        for store_link in store_links:
            file.write(store_link + "\n")

    print(f"[{state}] - Store links saved successfully")


def get_store_id_from_store_link(page: Page, store_link: str) -> str:
    """Create a new tab, navigate to the store, get the store ID, close the tab
    and return the store ID."""

    store_page = page.context.new_page()
    navigate_to_page(store_page, get_full_lowes_url(store_link))
    store_id = get_store_id(store_page)
    store_page.close()
    return store_id


def save_store_ids_for_state(store_ids: list[str], state: str) -> None:
    print(f"[{state}] - Saving store IDs")

    create_directory(STATES_STORES_IDS_DIR)
    store_ids_path = get_output_path(
        path.join(STATES_STORES_IDS_DIR, f"{state.lower()}_store_ids.txt")
    )
    with open(store_ids_path, "w", encoding="utf-8") as file:
        for store_id in store_ids:
            file.write(store_id + "\n")

    print(f"[{state}] - Store IDs saved successfully")


def process_all_state_stores_for_ids(
    page: Page, store_links: list[str], state: str
) -> None:
    """Process each store in the state and save the store IDs to a file."""
    print(f"[{state}] - Getting store IDs")

    store_ids: list[str] = []

    for store_link in store_links[:3]:
        store_id = get_store_id_from_store_link(page, store_link)
        store_ids.append(store_id)

    save_store_ids_for_state(store_ids, state)


def get_and_save_state_store_ids(playwright: Playwright) -> None:
    create_directory(STATES_STORES_LINKS_DIR)
    store_links = read_state_links()

    if not store_links:
        print("No state links found, exiting")
        return

    proxy_manager = ProxyManager()
    # page: Page
    page = get_page(playwright, proxy_manager.get_next_proxy())

    try:
        for state_link in store_links:
            state = state_link.split("/")[-2]
            # page = get_page(playwright, proxy_manager.get_next_proxy())

            store_links = get_state_store_links(page, state_link, state)

            process_all_state_stores_for_ids(page, store_links, state)
            # page.close()

    except Exception as e:
        print(f"Error while processing the page - {e}")

    finally:
        page.close()
