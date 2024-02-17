from typing import Callable, Optional

from playwright.sync_api import ElementHandle, Page, Playwright, sync_playwright
from playwright_stealth import stealth_sync

from constants import CHROMIUM_KWARGS
from utils.proxies import Proxy


def navigate_to_page(page: Page, url: str, debug: Optional[bool] = False) -> None:
    if debug:
        print(f"Navigating to {url.replace('\n', '')}")

    page.goto(url, wait_until="domcontentloaded")

    if debug:
        print(f"Arrived at {page.url}")


def get_el(page: Page, selector: str) -> ElementHandle:
    try:
        el = page.wait_for_selector(selector, timeout=3000, state="visible")

        if not el:
            raise Exception(f"Could not find selector {selector}")
        return el

    except Exception as e:
        raise Exception(f"Timed out: could not find selector {selector} - {e}") from e


def get_page(playwright: Playwright, proxy: Optional[Proxy] = None) -> Page:
    browser = playwright.chromium.launch(
        **CHROMIUM_KWARGS,
        proxy=(
            (
                {
                    "server": proxy.server,
                    "username": proxy.username,
                    "password": proxy.password,
                }
            )
            if proxy
            else None
        ),
    )
    context = browser.new_context()
    page = context.new_page()
    stealth_sync(page)
    return page


def run_playwright(process: Callable[[Playwright], None]) -> None:
    with sync_playwright() as playwright:
        process(playwright)
