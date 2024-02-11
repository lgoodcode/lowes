from typing import Callable
from playwright.sync_api import Page, sync_playwright


CHROMIUM_KWARGS = {
    "headless": False,
    "channel": "chrome",
    "args": [
        "--disable-http2",
        "--no-sandbox",
    ],
}


def navigate_to_page(page: Page, url: str) -> None:
    print(f"Navigating to {url}")
    page.goto(url, wait_until="domcontentloaded")
    print(f"Arrived at {page.url}")


def runner(process: Callable[[Page], None]) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**CHROMIUM_KWARGS)
        context = browser.new_context()
        page = context.new_page()

        try:
            process(page)

        except Exception as e:
            print(f"Error while processing the page - {e}")

        finally:
            browser.close()
