from typing import Any, Coroutine, List

from playwright.async_api import BrowserContext, Page

from lowes.constants import DEPARTMENT_LINKS_PATH, LOWES_STORES_URL
from lowes.utils.logger import get_logger
from lowes.utils.playwright import create_page, navigate_to_page
from lowes.utils.utils import get_full_lowes_url

logger = get_logger()


DEPARTMENT_SELECTOR = ".departments-container li.kuxg6u_engage-common-3.foDBid"
LOWES_DEPARTMENTS_URL = get_full_lowes_url("/departments")


async def get_department_links(page: Page) -> List[str]:
    logger.info("Getting state links")

    dept_link_els = await page.query_selector_all(DEPARTMENT_SELECTOR)
    links: List[str] = []

    for el in dept_link_els:
        if href := await el.get_attribute("href"):
            links.append(href)
    return links


def save_department_links(links: List[str]) -> None:
    logger.info("Saving department links")

    with open(DEPARTMENT_LINKS_PATH, "w", encoding="utf-8") as file:
        for link in links:
            file.write(link + "\n")


async def retrieve_department_links(
    context: BrowserContext,
) -> List[Coroutine[Any, Any, None]]:
    page = await create_page(context)

    async def task() -> None:
        await navigate_to_page(page, LOWES_STORES_URL)
        links = await get_department_links(page)
        save_department_links(links)

    return [task()]
