from unittest.mock import Mock, patch

import pytest
from playwright.async_api import Page

from lowes.utils.playwright import get_el, navigate_to_page


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
