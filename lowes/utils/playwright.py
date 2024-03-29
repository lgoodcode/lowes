from asyncio import sleep
from random import randint
from time import time
from typing import Union

from playwright.async_api import (
    Browser,
    BrowserContext,
    ElementHandle,
    Page,
    Playwright,
    ProxySettings,
)
from playwright_stealth import stealth_async

from lowes.constants import CHROMIUM_KWARGS, LOWES_URL
from lowes.utils.logger import get_logger
from lowes.utils.proxy import ProxyManager
from lowes.utils.retry import retry

logger = get_logger()


async def create_browser(playwright: Playwright, headless: bool = False) -> Browser:
    proxy = ProxyManager().get_next_proxy()
    browser = await playwright.chromium.launch(
        **CHROMIUM_KWARGS, headless=headless, proxy=ProxySettings(**proxy.__dict__)
    )
    return browser


async def create_context(playwright: Playwright) -> BrowserContext:
    browser = await create_browser(playwright)
    return await browser.new_context()


async def get_page(context: BrowserContext) -> Page:
    page = await context.new_page()
    await stealth_async(page)
    return page


async def create_page(playwright: Union[Playwright, BrowserContext]) -> Page:
    context = (
        playwright
        if isinstance(playwright, BrowserContext)
        else await create_context(playwright)
    )

    page = await context.new_page()
    await stealth_async(page)
    return page


@retry(delay=3, backoff=2)  # Extra delay in case the page was denied
async def navigate_to_page(page: Page, url: str) -> None:
    logger.debug(f"Navigating to {url.replace('\n', '')}")

    # Delay to simulate human behavior
    await sleep(randint(1, 3))
    await page.goto(url, wait_until="domcontentloaded", timeout=60_000)

    if (
        denied_el := await page.query_selector("body h1")
    ) and await denied_el.text_content() == "Access Denied":
        raise Exception(f"Access denied - {url}")

    logger.debug(f"Arrived at {page.url}")


@retry()
async def get_el(page: Page, selector: str, timeout: int = 10_000) -> ElementHandle:
    el = await page.wait_for_selector(selector, timeout=timeout, state="visible")

    if not el:
        raise Exception(f"Could not find selector {selector}")
    return el


async def set_store_cookie(page: Page, store_id: str) -> None:
    if LOWES_URL not in page.url:
        raise Exception(f"Cannot set cookie for non-Lowes page: {page.url}")

    await page.context.add_cookies(
        [
            {
                "name": "sn",
                "value": store_id,
                "domain": "www.lowes.com",
                "path": "/",
                "httpOnly": False,
                "secure": True,
                "expires": time() + 365 * 24 * 60 * 60,
            }
        ]
    )


async def change_store(page: Page, store_id: str) -> None:
    await set_store_cookie(page, store_id)
    await page.reload(wait_until="domcontentloaded")


async def get_store_name(page: Page) -> str:
    store_name_el = await get_el(page, "#store-search-handler")

    if not store_name_el:
        raise Exception("Could not find store name")

    if not (store_name := await store_name_el.text_content()):
        raise Exception("Could not find store name")

    return store_name.split(" ")[0]
