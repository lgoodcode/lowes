from asyncio import sleep
from random import randint
from typing import Any, Awaitable, Callable, Coroutine, List, Union

from playwright.async_api import (
    BrowserContext,
    ElementHandle,
    Page,
    Playwright,
    ProxySettings,
    async_playwright,
)
from playwright_stealth import stealth_async
from retry import retry

from lowes.constants import CHROMIUM_KWARGS
from lowes.utils.logger import get_logger
from lowes.utils.proxy import ProxyManager
from lowes.utils.tasks import batch_tasks

logger = get_logger()


@retry(tries=3, delay=1, backoff=2)
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


@retry(tries=3, delay=1, backoff=2)
async def get_el(page: Page, selector: str) -> ElementHandle:
    try:
        el = await page.wait_for_selector(selector, timeout=10_000, state="visible")

        if not el:
            raise Exception(f"Could not find selector {selector}")
        return el

    except Exception as e:
        raise Exception(f"[TIMEOUT]: Could not find selector {selector} - {e}") from e


async def create_context(playwright: Playwright) -> BrowserContext:
    proxy = ProxyManager().get_next_proxy()
    browser = await playwright.chromium.launch(
        **CHROMIUM_KWARGS, proxy=ProxySettings(**proxy.__dict__)
    )
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


async def async_run_with_context(
    process: Callable[[Playwright, int], Awaitable[List[Coroutine[Any, Any, None]]]],
    max_concurrency: int,
) -> None:
    async with async_playwright() as playwright:
        tasks = await process(playwright, max_concurrency)
        await batch_tasks(tasks, max_concurrency)
