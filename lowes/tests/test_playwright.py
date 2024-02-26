import pytest
from playwright.async_api import Page


@pytest.mark.asyncio
async def test_page_async(page: Page):
    await page.goto("https://playwright.dev/")
    assert (
        await page.title()
        == "Fast and reliable end-to-end testing for modern web apps | Playwright"
    )
