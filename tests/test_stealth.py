from playwright.async_api import Page


async def test_playwright_stealth_works(page: Page):
    await page.goto("https://bot.sannysoft.com")

    success_el = await page.query_selector_all(".passed")
    failed_el = await page.query_selector_all(".failed")

    assert success_el is not None
    assert failed_el is not None

    success_num = len(success_el)
    failed_num = len(failed_el)

    assert success_num / (success_num + failed_num) > 0.95
