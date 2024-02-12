from os import mkdir, path
from typing import Callable, Optional

from playwright.sync_api import Page, Playwright, sync_playwright

from constants import OUTPUT_DIR
from utils.proxies import Proxy, create_playwright_proxy_settings

LOWES_URL = "https://www.lowes.com"

CHROMIUM_KWARGS = {
    "headless": False,
    "channel": "chrome",
    "args": ["--no-sandbox", "--background"],
}


def get_output_path(file_path: str) -> str:
    """Return the path to a file in the /output directory."""
    create_directory(OUTPUT_DIR)  # Ensure output directory exists
    return path.join(OUTPUT_DIR, file_path)


def get_url(relative_url: str) -> str:
    if not relative_url.startswith("/"):
        relative_url = f"/{relative_url}"
    return f"https://www.lowes.com{relative_url}"


def create_directory(directory_path: str) -> None:
    """Create a directory if it does not exist in the /output directory."""

    if not directory_path.startswith(OUTPUT_DIR):
        directory_path = path.join(OUTPUT_DIR, directory_path)
    if not path.exists(directory_path):
        mkdir(directory_path)
        print(f"Directory created successfully: {directory_path}")


def navigate_to_page(page: Page, url: str) -> None:
    print(f"Navigating to {url.replace('\n', '')}")
    page.goto(url, wait_until="domcontentloaded")
    print(f"Arrived at {page.url}")


def get_page(playwright: Playwright, proxy: Optional[Proxy] = None) -> Page:
    browser = playwright.chromium.launch(
        **CHROMIUM_KWARGS,
        proxy=create_playwright_proxy_settings(proxy) if proxy else None,
    )
    context = browser.new_context()
    page = context.new_page()
    return page


def run_playwright(process: Callable[[Playwright], None]) -> None:
    with sync_playwright() as playwright:
        process(playwright)
