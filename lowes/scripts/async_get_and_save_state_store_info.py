from os import path
from typing import Any, Coroutine, List, Union

from playwright.async_api import BrowserContext, Page

from lowes.constants import (
    STATE_STORE_INFO_DIR,
    STATE_STORE_LINKS_PATH,
    STATE_STORES_LINKS_DIR,
)
from lowes.utils.async_playwright import get_el, get_page, navigate_to_page
from lowes.utils.logger import get_logger
from lowes.utils.tasks import batch_tasks
from lowes.utils.utils import create_directory, get_full_lowes_url

logger = get_logger()


STATES_STORES_IDS_DIR = "states_stores"
STORE_LINKS_SELECTOR = ".city-name a"
STORE_ADDRESS_SELECTOR = "#app #mainContent div header .address a"


class StoreInfo:
    def __init__(
        self,
        store_id: str,
        address: str,
        city: str,
        state: str,
        zipcode: str,
    ):
        self.store_id = store_id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode

    def __str__(self):
        return f"{self.store_id},{self.address},{self.city},{self.state},{self.zipcode}"


async def parse_store_page(page: Page, store_id: str) -> StoreInfo:
    store_address_el = await get_el(page, STORE_ADDRESS_SELECTOR)
    store_address = await store_address_el.get_attribute("href")

    if not store_address:
        raise Exception("Could not find store address")

    raw_store_address = store_address.split("=")[-1].replace(",", "")
    (address, city, state, zipcode) = raw_store_address.split("+")

    if not address or not city or not state or not zipcode:
        raise Exception("Could not parse store address")

    store_info = StoreInfo(store_id, address, city, state, zipcode)
    return store_info


def read_state_links() -> List[str]:
    logger.info("Reading state links")
    with open(STATE_STORE_LINKS_PATH, "r", encoding="utf-8") as file:
        state_links = file.readlines()
    return state_links


async def get_store_links(page: Page) -> List[str]:
    store_link_els = await page.query_selector_all(STORE_LINKS_SELECTOR)
    store_links: List[str] = []

    for store_link in store_link_els:
        if href := await store_link.get_attribute("href"):
            store_links.append(href)
    return store_links


async def get_state_store_links(page: Page, state_link: str, state: str) -> List[str]:
    """Navigate to list of all stores in the state, get all the store links,
    save them to a file, and return them."""

    await navigate_to_page(page, get_full_lowes_url(state_link))
    store_links = await get_store_links(page)
    save_store_links(store_links, state)
    return store_links


def save_store_links(store_links: List[str], state: str) -> None:
    logger.info(f"[{state}] - Saving store links")

    create_directory(STATE_STORES_LINKS_DIR)
    file_path = path.join(STATE_STORES_LINKS_DIR, f"{state.lower()}_store_links.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        for store_link in store_links:
            file.write(store_link + "\n")

    logger.info(f"[{state}] - Store links saved successfully")


async def process_store_page(page: Page, state: str, store_link: str) -> StoreInfo:
    """Create a new tab, navigate to the store, get the store info, close the tab
    and return the store info."""

    store_id = store_link.split("/")[-1]
    logger.info(f"[{state}] - Getting store info for {store_id}")

    store_page = await page.context.new_page()
    await navigate_to_page(store_page, get_full_lowes_url(store_link))
    store_info = await parse_store_page(store_page, store_id)
    await store_page.close()
    return store_info


def save_store_infos_for_state(store_infos: List[StoreInfo], state: str) -> None:
    logger.info(f"[{state}] - Saving store info")

    create_directory(STATE_STORE_INFO_DIR)
    file_path = path.join(STATE_STORE_INFO_DIR, f"{state.lower()}_stores.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        for store_info in store_infos:
            file.write(str(store_info) + "\n")

    logger.info(f"[{state}] - All store info saved successfully")


async def process_all_state_stores(
    page: Page, store_links: List[str], state: str
) -> None:
    """Process each store in the state and save the store info to a file."""

    logger.info(f"[{state}] - Getting store info")

    store_infos: List[StoreInfo] = []

    # Batch the store links to check multiple at once
    async def task(store_link: str):
        store_info = await process_store_page(page, state, store_link)
        store_infos.append(store_info)

    tasks = [task(store_link) for store_link in store_links]
    await batch_tasks(tasks)

    save_store_infos_for_state(store_infos, state)


async def get_store_infos_for_state(context: BrowserContext, state_link: str) -> None:
    state = state_link.split("/")[-2]
    page: Union[Page, None] = None

    try:
        page = await get_page(context)
        store_links = await get_state_store_links(page, state_link, state)
        await process_all_state_stores(page, store_links, state)
        await page.close()

    except Exception as e:
        logger.error(f"[{state}]: Error processing {state_link}: {e}")

    finally:
        if page:
            await page.close()


async def async_get_and_save_state_store_info(
    context: BrowserContext,
) -> List[Coroutine[Any, Any, None]]:
    create_directory(STATE_STORE_LINKS_PATH)
    state_links = read_state_links()

    if not state_links:
        logger.info("No state links found, exiting")
        exit(1)

    tasks = [
        get_store_infos_for_state(context, state_link) for state_link in state_links
    ]

    return tasks
