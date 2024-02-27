from unittest.mock import Mock, mock_open, patch

from playwright.async_api import BrowserContext, Page

from lowes.constants import LOWES_STORES_URL
from lowes.scripts.retrieve_store_links import (
    STATE_STORE_LINKS_PATH,
    get_state_links,
    retrieve_store_links,
    save_state_links,
)
from lowes.utils.playwright import navigate_to_page

NUM_STATE_LINKS = 51


async def test_lowes_get_state_links(page: Page):
    await navigate_to_page(page, LOWES_STORES_URL)
    links = await get_state_links(page)
    assert len(links) == 51


@patch("builtins.open", new_callable=mock_open)
def test_save_state_links(mock_open_arg: Mock):
    state_links = ["link1", "link2"]

    save_state_links(state_links)

    # Assert that the mocked file was opened with correct parameters
    mock_open_arg.assert_called_once_with(STATE_STORE_LINKS_PATH, "w", encoding="utf-8")
    handle = mock_open_arg()

    handle.write.assert_any_call("link1\n")
    handle.write.assert_any_call("link2\n")
    assert handle.write.call_count == 2


@patch("builtins.open", new_callable=mock_open)
async def test_retrieve_store_links(mock_open_arg: Mock, context: BrowserContext):
    (task,) = await retrieve_store_links(context)
    await task
    mock_open_arg.assert_called_once_with(STATE_STORE_LINKS_PATH, "w", encoding="utf-8")
    handle = mock_open_arg()
    assert handle.write.call_count == NUM_STATE_LINKS
