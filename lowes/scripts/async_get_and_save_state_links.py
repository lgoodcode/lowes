from playwright.async_api import Page, Playwright

from lowes.constants import LOWES_STORES_URL
from lowes.utils.async_playwright import create_page, navigate_to_page
from lowes.utils.logger import get_logger
from lowes.utils.proxies import ProxyManager
from lowes.utils.utils import get_output_path

logger = get_logger()

STATE_LINK_QUERY = "div[data-selector='str-storeDetailContainer'] .backyard.link"


async def get_state_links(page: Page) -> list[str]:
    logger.info("Getting state links")

    raw_state_link_els = await page.query_selector_all(STATE_LINK_QUERY)
    # Skip the first two links, they are not states
    state_link_els = raw_state_link_els[2:]
    state_links: list[str] = []

    for state_link_el in state_link_els:
        if href := await state_link_el.get_attribute("href"):
            state_links.append(href)
    return state_links


def save_state_links(state_links: list[str]) -> None:
    logger.info("Saving state links")

    with open(get_output_path("state_links.txt"), "w", encoding="utf-8") as file:
        for state_link in state_links:
            file.write(state_link + "\n")


async def async_get_and_save_state_links(playwright: Playwright) -> None:
    proxy_manager = ProxyManager()
    page = await create_page(playwright, proxy_config=proxy_manager.get_next_proxy())

    try:
        await navigate_to_page(page, LOWES_STORES_URL)
        state_links = await get_state_links(page)
        save_state_links(state_links)

    except Exception as e:
        logger.error(f"Error while processing the page - {e}")

    finally:
        await page.close()
