from typing import Any, Coroutine, List

from playwright.async_api import BrowserContext, Page

from lowes.constants import LOWES_STORES_URL, STATE_STORE_LINKS_PATH
from lowes.utils.logger import get_logger
from lowes.utils.playwright import create_page, navigate_to_page

logger = get_logger()

STATE_LINK_QUERY = "div[data-selector='str-storeDetailContainer'] .backyard.link"


async def get_state_links(page: Page) -> List[str]:
    logger.info("Getting state links")

    raw_state_link_els = await page.query_selector_all(STATE_LINK_QUERY)
    # Skip the first two links, they are not states
    state_link_els = raw_state_link_els[2:]
    state_links: List[str] = []

    for state_link_el in state_link_els:
        if href := await state_link_el.get_attribute("href"):
            state_links.append(href)
    return state_links


def save_state_links(state_links: List[str]) -> None:
    logger.info("Saving state links")

    with open(STATE_STORE_LINKS_PATH, "w", encoding="utf-8") as file:
        for state_link in state_links:
            file.write(state_link + "\n")


async def retrieve_store_links(
    context: BrowserContext,
) -> List[Coroutine[Any, Any, None]]:
    page = await create_page(context)

    async def task() -> None:
        await navigate_to_page(page, LOWES_STORES_URL)
        state_links = await get_state_links(page)
        save_state_links(state_links)

    return [task()]
