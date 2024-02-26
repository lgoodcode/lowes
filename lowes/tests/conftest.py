import asyncio
from typing import Any, AsyncGenerator, Awaitable, Callable, List

import pytest
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from lowes.utils.playwright import create_browser


# https://pytest-asyncio.readthedocs.io/en/latest/reference/fixtures/index.html
# Custom event loop by redfining the event_loop fixture.
# If the test is marked with @pytest.mark.asyncio, it will use this event loop.
@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def playwright() -> AsyncGenerator[Playwright, None]:
    async with async_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
async def browser_factory(
    playwright: Playwright,
) -> AsyncGenerator[Callable[..., Awaitable[Browser]], None]:
    browsers: List[Browser] = []

    async def launch() -> Browser:
        browser = await create_browser(playwright)
        browsers.append(browser)
        return browser

    yield launch
    for browser in browsers:
        await browser.close()


@pytest.fixture
async def browser(
    browser_factory: Callable[..., asyncio.Future[Browser]],
) -> AsyncGenerator[Browser, None]:
    browser = await browser_factory()
    yield browser
    await browser.close()


@pytest.fixture
async def context_factory(
    browser: Browser,
) -> AsyncGenerator[Callable[..., Awaitable[BrowserContext]], None]:
    contexts: List[BrowserContext] = []

    async def launch(**kwargs: Any) -> BrowserContext:
        context = await browser.new_context(**kwargs)
        contexts.append(context)
        return context

    yield launch
    for context in contexts:
        await context.close()


@pytest.fixture
async def context(
    context_factory: Callable[..., asyncio.Future[BrowserContext]],
) -> AsyncGenerator[BrowserContext, None]:
    context = await context_factory()
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext) -> AsyncGenerator[Page, None]:
    page = await context.new_page()
    yield page
    await page.close()
