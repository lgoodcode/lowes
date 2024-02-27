from asyncio import sleep
from random import randint
from typing import Any, Awaitable, Callable, Coroutine, List, Union

from playwright.async_api import (
    Browser,
    BrowserContext,
    ElementHandle,
    Page,
    Playwright,
    ProxySettings,
    async_playwright,
)
from playwright_stealth import stealth_async

from lowes.constants import CHROMIUM_KWARGS
from lowes.utils.logger import get_logger
from lowes.utils.proxy import ProxyManager
from lowes.utils.retry import retry
from lowes.utils.tasks import batch_tasks

logger = get_logger()


@retry()
async def get_el(page: Page, selector: str, timeout: int = 10_000) -> ElementHandle:
    el = await page.wait_for_selector(selector, timeout=timeout, state="visible")

    if not el:
        raise Exception(f"Could not find selector {selector}")
    return el


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


async def run_with_context(
    process: Callable[[Playwright, int], Awaitable[List[Coroutine[Any, Any, None]]]],
    max_concurrency: int,
) -> None:
    async with async_playwright() as playwright:
        tasks = await process(playwright, max_concurrency)
        await batch_tasks(tasks, max_concurrency)
