from unittest.mock import Mock, mock_open, patch

import pytest
from playwright.async_api import BrowserContext, Page

from lowes.constants import LOWES_STORES_URL
from lowes.scripts.retrieve_store_links import (
    STATE_STORE_LINKS_PATH,
    StateLinkRetriever,
)
from lowes.utils.playwright import navigate_to_page

NUM_STATE_LINKS = 51


async def test_lowes_get_state_links(page: Page):
    client = StateLinkRetriever()
    await navigate_to_page(page, LOWES_STORES_URL)
    await client.get_links(page)
    assert len(client.links) == 51


def test_no_len_save_links():
    client = StateLinkRetriever()
    client.links = []
    with pytest.raises(Exception) as e:
        client.save_links()
        assert "No links to save" in str(e)


@patch("builtins.open", new_callable=mock_open)
def test_save_state_links(mock_open_arg: Mock):
    test_links = ["link1", "link2"]

    client = StateLinkRetriever()
    client.links = test_links
    client.save_links()

    # Assert that the mocked file was opened with correct parameters
    mock_open_arg.assert_called_once_with(STATE_STORE_LINKS_PATH, "w", encoding="utf-8")
    handle = mock_open_arg()

    test_link_str = "".join([link + "\n" for link in test_links])
    assert test_link_str == handle.write.call_args_list[0].args[0]
    assert handle.write.call_count == 1


@patch("builtins.open", new_callable=mock_open)
async def test_main(mock_open_arg: Mock, context: BrowserContext):
    await StateLinkRetriever().main(1)
    mock_open_arg.assert_called_once_with(STATE_STORE_LINKS_PATH, "w", encoding="utf-8")
    handle = mock_open_arg()
    assert handle.write.call_count == 1
