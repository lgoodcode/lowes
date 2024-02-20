from typing import Awaitable, Callable, Optional, Union, overload

from playwright.async_api import (
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
from lowes.utils.proxies import Proxy

logger = get_logger()


async def navigate_to_page(page: Page, url: str) -> None:
    logger.debug(f"Navigating to {url.replace('\n', '')}")

    await page.goto(url, wait_until="domcontentloaded")

    logger.debug(f"Arrived at {page.url}")


async def get_el(page: Page, selector: str) -> ElementHandle:
    try:
        el = await page.wait_for_selector(selector, timeout=3000, state="visible")

        if not el:
            raise Exception(f"Could not find selector {selector}")
        return el

    except Exception as e:
        raise Exception(f"Timed out: could not find selector {selector} - {e}") from e


async def create_context(
    playwright: Playwright, proxy_config: Optional[Proxy] = None
) -> BrowserContext:
    browser = await playwright.chromium.launch(
        **CHROMIUM_KWARGS,
        proxy=(
            ProxySettings(
                server=proxy_config.server,
                username=proxy_config.username,
                password=proxy_config.password,
            )
            if proxy_config
            else None
        ),
    )

    return await browser.new_context()


async def get_page(context: BrowserContext) -> Page:
    page = await context.new_page()
    await stealth_async(page)
    return page


@overload
async def create_page(
    playwright: Playwright, proxy_config: Optional[Proxy] = None
) -> Page: ...


@overload
async def create_page(playwright: BrowserContext) -> Page: ...


async def create_page(
    playwright: Union[Playwright, BrowserContext], proxy_config: Optional[Proxy] = None
) -> Page:
    context = (
        playwright
        if isinstance(playwright, BrowserContext)
        else await create_context(playwright, proxy_config)
    )

    page = await context.new_page()
    await stealth_async(page)
    return page


async def async_run_with_playwright(
    process: Callable[[Playwright], Awaitable[None]]
) -> None:
    async with async_playwright() as playwright:
        await process(playwright)
