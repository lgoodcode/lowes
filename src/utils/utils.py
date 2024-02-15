from os import mkdir, path
from typing import Callable, Optional

from playwright.sync_api import ElementHandle, Page, Playwright, sync_playwright
from playwright_stealth import stealth_sync

from constants import OUTPUT_DIR
from utils.proxies import Proxy, create_playwright_proxy_settings

LOWES_URL = "https://www.lowes.com"
CHROMIUM_KWARGS = {
    "headless": False,
    "channel": "chrome",
    "args": ["--disable-http2", "--no-sandbox", "--background"],
}


def get_output_path(file_path: str) -> str:
    """Return the path to a file in the /output directory."""

    create_directory(OUTPUT_DIR)  # Ensure output directory exists
    return path.join(OUTPUT_DIR, file_path)


def get_url(relative_url: str) -> str:
    if relative_url.startswith("/"):
        relative_url = relative_url[1:]
    return f"{LOWES_URL}/{relative_url}"


def create_directory(directory_path: str) -> None:
    """Create a directory if it does not exist in the /output directory."""

    if not directory_path.startswith(OUTPUT_DIR):
        directory_path = path.join(OUTPUT_DIR, directory_path)
    if not path.exists(directory_path):
        mkdir(directory_path)
        print(f"Directory created successfully: {directory_path}")


def navigate_to_page(page: Page, url: str, debug=False) -> None:
    if debug:
        print(f"Navigating to {url.replace('\n', '')}")

    page.goto(url, wait_until="domcontentloaded")

    if debug:
        print(f"Arrived at {page.url}")


def get_page(playwright: Playwright, proxy: Optional[Proxy] = None) -> Page:
    browser = playwright.chromium.launch(
        **CHROMIUM_KWARGS,
        proxy=create_playwright_proxy_settings(proxy) if proxy else None,
    )
    context = browser.new_context()
    page = context.new_page()
    stealth_sync(page)
    return page


def run_playwright(process: Callable[[Playwright], None]) -> None:
    with sync_playwright() as playwright:
        process(playwright)


def get_el(page: Page, selector: str) -> ElementHandle:
    try:
        el = page.wait_for_selector(selector, timeout=3000, state="visible")
        return el
    except Exception as e:
        raise Exception(f"Could not find selector {selector} - {e}") from e
