from typing import Dict
from unittest.mock import Mock, patch

import pytest
from playwright.async_api import Page

from lowes.constants import LOWES_URL
from lowes.utils.playwright import (
    change_store,
    get_el,
    get_store_name,
    navigate_to_page,
    set_store_cookie,
)
from lowes.utils.retry import retry

TEST_STORE_1 = {"id": "2525", "city": "Alabaster"}

TEST_STORE_2 = {"id": "2659", "city": "Anniston"}


@patch(
    "playwright.async_api.Page.wait_for_selector",
    return_value=None,
)
async def test_get_el_error_retries(mock_wait_for_selector: Mock, page: Page):
    with pytest.raises(Exception) as e:
        await get_el(page, "selector")

    assert "Could not find selector" in str(e.value)
    assert mock_wait_for_selector.call_count == 3


async def test_navigate_to_page(page: Page):
    await navigate_to_page(page, "https://google.com")
    assert await page.title() == "Google"


async def test_navigate_to_page_denied_retries(page: Page):
    tracker = {"retry_count": 0}

    @retry()
    async def test_navigate_to_page(page: Page, tracker: Dict[str, int]) -> None:
        await page.evaluate(f"document.write('<h1>Access Denied</h1>')")
        if (
            denied_el := await page.query_selector("body h1")
        ) and await denied_el.text_content() == f"Access Denied":
            tracker["retry_count"] += 1
            raise Exception(f"Access denied")

    with pytest.raises(Exception):
        await test_navigate_to_page(page, tracker)
    assert tracker["retry_count"] == 3


async def test_set_store_cookie_error_on_non_lowes_page(page: Page):
    await navigate_to_page(page, "https://google.com")

    with pytest.raises(Exception) as e:
        await set_store_cookie(page, TEST_STORE_1["id"])
    assert "Cannot set cookie for non-Lowes page" in str(e.value)


async def test_set_store_cookie(page: Page):
    await navigate_to_page(page, LOWES_URL)
    await set_store_cookie(page, TEST_STORE_1["id"])
    await page.reload(wait_until="domcontentloaded")

    cookies = await page.context.cookies()
    store_cookie = [c for c in cookies if c.get("name") == "sn"]

    assert len(store_cookie)
    assert store_cookie[0].get("value") == TEST_STORE_1["id"]
    assert await get_store_name(page) == TEST_STORE_1["city"]


async def test_change_store(page: Page):
    await navigate_to_page(page, LOWES_URL)
    await change_store(page, TEST_STORE_1["id"])
    assert await get_store_name(page) == TEST_STORE_1["city"]
    await change_store(page, TEST_STORE_2["id"])
    assert await get_store_name(page) == TEST_STORE_2["city"]
