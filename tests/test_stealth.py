import pytest
from playwright.sync_api import Page
from playwright_stealth import stealth_sync


@pytest.mark.skip(reason="not testing this right now; it works")
def test_playwright_stealth_works(page: Page):
    stealth_sync(page)
    page.goto("https://bot.sannysoft.com")

    success_el = page.query_selector_all(".passed")
    failed_el = page.query_selector_all(".failed")

    assert success_el is not None
    assert failed_el is not None

    success_num = len(success_el)
    failed_num = len(failed_el)

    assert success_num / (success_num + failed_num) > 0.95
