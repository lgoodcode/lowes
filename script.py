from playwright.sync_api import Playwright, sync_playwright, Page, ElementHandle
from playwright_stealth import stealth_sync

CHROMIUM_KWARGS = {
    "headless": False,
    "channel": "chrome",
    "args": [
        "--disable-http2",
        "--no-sandbox",
    ],
}

STORES_LIST = [
    "https://www.lowes.com/store/AL-Alabaster/2525",
]

STORE_ID_SELECTOR = "span.storeNo2"


def navigate_to_store(page: Page, store_url: str) -> None:
    print(f"Navigating to {store_url}")
    page.goto(store_url, wait_until="domcontentloaded")
    print(f"Arrived at {page.url}")


def get_el(page: Page, selector: str) -> ElementHandle:
    try:
        el = page.wait_for_selector(selector, timeout=3000)
        return el
    except Exception as e:
        raise Exception(f"Could not find selector {selector} - {e}") from e


def get_store_id(page: Page) -> str:
    store_id_el = get_el(page, STORE_ID_SELECTOR)
    raw_store_id_text = store_id_el.inner_text()
    store_id = raw_store_id_text.split("#")[1]
    return store_id


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(**CHROMIUM_KWARGS)
    context = browser.new_context()
    page = context.new_page()
    stealth_sync(page)

    try:
        for store in STORES_LIST:
            navigate_to_store(page, store)
            store_id = get_store_id(page)

    except Exception as e:
        print(f"Error [{store}] - {e}")

    finally:
        # Ensure the browser is always closed
        browser.close()


with sync_playwright() as p:
    run(p)
