from typing import List

from playwright.async_api import Page, Playwright

from lowes.constants import LOWES_STORES_URL, STATE_STORE_LINKS_PATH
from lowes.utils.classes import TaskRunner
from lowes.utils.playwright import create_page, navigate_to_page

STATE_LINK_QUERY = "div[data-selector='str-storeDetailContainer'] .backyard.link"


async def get_state_links(page: Page) -> List[str]:
    raw_state_link_els = await page.query_selector_all(STATE_LINK_QUERY)
    # Skip the first two links, they are not states
    state_link_els = raw_state_link_els[2:]
    links: List[str] = []

    for state_link_el in state_link_els:
        if href := await state_link_el.get_attribute("href"):
            links.append(href)
    return links


def save_state_links(file_path: str, links: List[str]):
    with open(file_path, "w", encoding="utf-8") as file:
        for link in links:
            file.write(link + "\n")


class StateLinkRetriever(TaskRunner):
    links: List[str]

    def __init__(self):
        super().__init__()

    async def get_links(self, page: Page):
        self.logger.info("Getting state links")
        self.links = await get_state_links(page)

    def save_links(self, links: List[str]):
        self.logger.info("Saving state links")

        if len(links) == 0:
            raise Exception("No links to save, exiting")

        save_state_links(STATE_STORE_LINKS_PATH, self.links)

    async def task(self, page: Page) -> None:
        await navigate_to_page(page, LOWES_STORES_URL)
        await self.get_links(page)
        self.save_links(self.links)

    async def create_tasks(self, playwright: Playwright, max_contexts: int):
        self.tasks.append(self.task(await create_page(playwright)))
