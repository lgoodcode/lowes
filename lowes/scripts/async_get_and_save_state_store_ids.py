import asyncio
from os import path
from typing import Any, Coroutine, List

from playwright.async_api import BrowserContext, Page

from lowes.utils.async_playwright import get_el, get_page, navigate_to_page
from lowes.utils.logger import get_logger
from lowes.utils.utils import create_directory, get_full_lowes_url, get_output_path

logger = get_logger()

# MAX_CONCURRENCY = 3
STATES_STORES_LINKS_DIR = "states_stores_links"
STATES_STORES_IDS_DIR = "states_stores_ids"
STORE_LINKS_SELECTOR = ".city-name a"
STORE_ID_SELECTOR = "span.storeNo"


async def get_store_id(page: Page) -> str:
    store_id_el = await get_el(page, STORE_ID_SELECTOR)
    raw_store_id_text = await store_id_el.inner_text()
    store_id = raw_store_id_text.split("#")[1]
    return store_id


def read_state_links() -> List[str]:
    logger.info("Reading state links")
    with open(get_output_path("state_links.txt"), "r", encoding="utf-8") as file:
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

    create_directory(STATES_STORES_LINKS_DIR)
    state_links_path = get_output_path(
        path.join(STATES_STORES_LINKS_DIR, f"{state.lower()}_store_links.txt")
    )
    with open(state_links_path, "w", encoding="utf-8") as file:
        for store_link in store_links:
            file.write(store_link + "\n")

    logger.info(f"[{state}] - Store links saved successfully")


async def get_store_id_from_store_link(page: Page, store_link: str) -> str:
    """Create a new tab, navigate to the store, get the store ID, close the tab
    and return the store ID."""

    store_page = await page.context.new_page()
    await navigate_to_page(store_page, get_full_lowes_url(store_link))
    store_id = await get_store_id(store_page)
    await store_page.close()
    return store_id


def save_store_ids_for_state(store_ids: List[str], state: str) -> None:
    logger.info(f"[{state}] - Saving store IDs")

    create_directory(STATES_STORES_IDS_DIR)
    store_ids_path = get_output_path(
        path.join(STATES_STORES_IDS_DIR, f"{state.lower()}_store_ids.txt")
    )
    with open(store_ids_path, "w", encoding="utf-8") as file:
        for store_id in store_ids:
            file.write(store_id + "\n")

    logger.info(f"[{state}] - Store IDs saved successfully")


async def process_all_state_stores_for_ids(
    page: Page, store_links: List[str], state: str
) -> None:
    """Process each store in the state and save the store IDs to a file."""

    logger.info(f"[{state}] - Getting store IDs")

    store_ids: List[str] = []

    # Batch the store links to check multiple at once
    async def task(store_link: str):
        store_id = await get_store_id_from_store_link(page, store_link)
        store_ids.append(store_id)

    tasks = [task(store_link) for store_link in store_links[:3]]
    await asyncio.gather(*tasks)

    save_store_ids_for_state(store_ids, state)


async def get_store_ids_for_state(context: BrowserContext, state_link: str) -> None:
    try:
        page = await get_page(context)
        state = state_link.split("/")[-2]
        store_links = await get_state_store_links(page, state_link, state)
        await process_all_state_stores_for_ids(page, store_links, state)
        await page.close()

    except Exception as e:
        raise e


async def async_get_and_save_state_store_ids(
    context: BrowserContext,
) -> List[Coroutine[Any, Any, None]]:
    create_directory(STATES_STORES_LINKS_DIR)
    state_links = read_state_links()

    if not state_links:
        logger.info("No state links found, exiting")
        exit(1)

    tasks = [
        get_store_ids_for_state(context, state_link) for state_link in state_links[:3]
    ]

    return tasks