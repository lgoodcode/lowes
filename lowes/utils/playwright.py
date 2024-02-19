from typing import Callable, Optional

from playwright.sync_api import (
    BrowserContext,
    ElementHandle,
    Page,
    Playwright,
    ProxySettings,
    sync_playwright,
)
from playwright_stealth import stealth_sync

from lowes.constants import CHROMIUM_KWARGS
from lowes.utils.logger import get_logger
from lowes.utils.proxies import Proxy

logger = get_logger()


def navigate_to_page(page: Page, url: str) -> None:
    logger.debug(f"Navigating to {url.replace('\n', '')}")

    page.goto(url, wait_until="domcontentloaded")

    logger.debug(f"Arrived at {page.url}")


def get_el(page: Page, selector: str) -> ElementHandle:
    try:
        el = page.wait_for_selector(selector, timeout=3000, state="visible")

        if not el:
            raise Exception(f"Could not find selector {selector}")
        return el

    except Exception as e:
        raise Exception(f"Timed out: could not find selector {selector} - {e}") from e


def create_context(
    playwright: Playwright, proxy_config: Optional[Proxy] = None
) -> BrowserContext:
    browser = playwright.chromium.launch(
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

    return browser.new_context()


def get_page(context: BrowserContext) -> Page:
    page = context.new_page()
    stealth_sync(page)
    return context.new_page()


def create_page(playwright: Playwright, proxy_config: Optional[Proxy] = None) -> Page:
    context = create_context(playwright, proxy_config)
    page = context.new_page()
    stealth_sync(page)
    return page


def run_with_playwright(process: Callable[[Playwright], None]) -> None:
    with sync_playwright() as playwright:
        process(playwright)
