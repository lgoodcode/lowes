import asyncio

from playwright.async_api import async_playwright
from playwright_stealth import stealth_async


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        await stealth_async(page)
        await page.goto("https://bot.sannysoft.com")
        await asyncio.sleep(10_000)
        await browser.close()


asyncio.run(main())
