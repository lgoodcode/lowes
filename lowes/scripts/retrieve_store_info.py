from os import path
from typing import List

from playwright.async_api import BrowserContext, Page, Playwright

from lowes.constants import (
    STATE_STORE_INFO_DIR,
    STATE_STORE_LINKS_PATH,
    STATE_STORES_LINKS_DIR,
)
from lowes.utils.classes import TaskRunner
from lowes.utils.playwright import create_context, get_el, get_page, navigate_to_page
from lowes.utils.tasks import batch_tasks
from lowes.utils.utils import create_directory, get_full_lowes_url

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


def read_state_links(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()


def save_store_links(parent_file_path: str, store_links: List[str], state: str) -> None:
    create_directory(parent_file_path)
    file_path = path.join(parent_file_path, f"{state.lower()}_store_links.txt")

    with open(file_path, "w", encoding="utf-8") as file:
        for store_link in store_links:
            file.write(store_link + "\n")


async def get_store_links(page: Page) -> List[str]:
    store_link_els = await page.query_selector_all(STORE_LINKS_SELECTOR)
    store_links: List[str] = []

    for store_link in store_link_els:
        if href := await store_link.get_attribute("href"):
            store_links.append(href)
    return store_links


class StateStoreInfoRetriever(TaskRunner):
    state_links: List[str]

    def __init__(self):
        super().__init__()
        self.state_links = self.read_state_links()

        if not self.state_links:
            self.logger.info("No state links found, exiting")
            exit(1)

        create_directory(STATE_STORE_LINKS_PATH)

    def read_state_links(self) -> List[str]:
        self.logger.info("Reading state links")
        return read_state_links(STATE_STORE_LINKS_PATH)

    def save_store_links(self, store_links: List[str], state: str) -> None:
        self.logger.info(f"[{state}] - Saving store links")

        save_store_links(
            parent_file_path=STATE_STORES_LINKS_DIR,
            store_links=store_links,
            state=state,
        )

        self.logger.info(f"[{state}] - Store links saved successfully")

    async def get_state_store_links(
        self, page: Page, state_link: str, state: str
    ) -> List[str]:
        """Navigate to list of all stores in the state, get all the store links,
        save them to a file, and return them."""

        await navigate_to_page(page, get_full_lowes_url(state_link))
        store_links = await get_store_links(page)
        self.save_store_links(store_links, state)
        return store_links

    def save_store_infos_for_state(
        self, store_infos: List[StoreInfo], state: str
    ) -> None:
        self.logger.info(f"[{state}] - Saving store info")

        create_directory(STATE_STORE_INFO_DIR)
        file_path = path.join(STATE_STORE_INFO_DIR, f"{state.lower()}_stores.txt")

        with open(file_path, "w", encoding="utf-8") as file:
            for store_info in store_infos:
                file.write(str(store_info) + "\n")

        self.logger.info(f"[{state}] - All store info saved successfully")

    async def parse_store_page(self, page: Page, store_id: str) -> StoreInfo:
        store_address_el = await get_el(page, STORE_ADDRESS_SELECTOR)
        store_address = await store_address_el.get_attribute("href")

        if not store_address:
            raise Exception("Could not find store address")

        raw_store_address = store_address.split("=")[-1].replace(",", "")
        (address, city, state, zipcode) = raw_store_address.split("+")

        if not address or not city or not state or not zipcode:
            raise Exception("Could not parse store address")

        return StoreInfo(store_id, address, city, state, zipcode)

    async def process_store_page(
        self, page: Page, store_link: str, store_id: str
    ) -> StoreInfo:
        """Create a new tab, navigate to the store, get the store info, close the tab
        and return the store info."""

        store_page = await page.context.new_page()
        await navigate_to_page(store_page, get_full_lowes_url(store_link))
        store_info = await self.parse_store_page(page=store_page, store_id=store_id)
        await store_page.close()
        return store_info

    async def process_all_state_stores(
        self, page: Page, store_links: List[str], state: str
    ) -> None:
        """Process each store in the state and save the store info to a file."""

        self.logger.info(f"[{state}] - Getting store info")
        store_infos: List[StoreInfo] = []

        # Batch the store links to check multiple at once
        async def task(store_link: str):
            store_id = store_link.split("/")[-1]
            self.logger.info(f"[{state}] - Getting store info for {store_id}")
            store_info = await self.process_store_page(
                page, store_link=store_link, store_id=store_id
            )
            store_infos.append(store_info)

        tasks = [task(store_link) for store_link in store_links]
        await batch_tasks(tasks)

        self.save_store_infos_for_state(store_infos, state)

    async def get_store_infos_for_state(
        self, context: BrowserContext, state_link: str
    ) -> None:
        state = state_link.split("/")[-2]
        page = await get_page(context)

        try:
            store_links = await self.get_state_store_links(
                page, state_link=state_link, state=state
            )
            await self.process_all_state_stores(
                page, store_links=store_links, state=state
            )

        except Exception as e:
            self.logger.error(f"[{state}] - {e}")

        finally:
            await page.close()

    async def create_tasks(self, playwright: Playwright, max_contexts: int) -> None:
        contexts = [await create_context(playwright) for _ in range(max_contexts)]

        for i, link in enumerate(self.state_links):
            context = contexts[i % len(contexts)]  # Round robin assignment
            self.tasks.append(self.get_store_infos_for_state(context, link))
