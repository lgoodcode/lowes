from os import path
from typing import List
from unittest.mock import Mock, mock_open, patch

from playwright.async_api import BrowserContext, Page

from lowes.constants import STATE_STORES_LINKS_DIR
from lowes.scripts.retrieve_store_info import (
    StateStoreInfoRetriever,
    StoreInfo,
    save_store_links,
)
from lowes.utils.playwright import navigate_to_page
from lowes.utils.utils import get_full_lowes_url

STATE = "Alabama"
STORE_DATA = [
    "2525,235 Colonial Promenade Pkwy,Alabaster,AL,35007",
    "2659,4901 Mcclellan Boulevard,Anniston,AL,36206",
    "1799,1109 Us Highway 72 East,Athens,AL,35611",
    "1531,1201 19TH Street North,Bessemer,AL,35020",
]
STORE_LINKS = [
    "/store/AL-Alabaster/2525",
    "/store/AL-Anniston/2659",
    "/store/AL-Athens/1799",
    "/store/AL-Bessemer/1531",
]
STATE_LINK = "/Lowes-Stores/Alabama/AL"

TEST_STORES: List[StoreInfo] = [StoreInfo(*data.split(",")) for data in STORE_DATA]


@patch("builtins.open", new_callable=mock_open)
async def test_save_store_links(mock_open_arg: Mock):
    mock_store_links = STORE_LINKS
    mock_state = STATE

    save_store_links(
        parent_file_path=STATE_STORES_LINKS_DIR,
        store_links=mock_store_links,
        state=mock_state,
    )

    mock_file_path = path.join(
        STATE_STORES_LINKS_DIR, f"{mock_state.lower()}_store_links.txt"
    )

    # Assert that the mocked file was opened with correct parameters
    mock_open_arg.assert_called_once_with(mock_file_path, "w", encoding="utf-8")
    handle = mock_open_arg()

    for link in mock_store_links:
        handle.write.assert_any_call(link + "\n")
    assert handle.write.call_count == len(mock_store_links)


async def test_parse_store_page(page: Page):
    client = StateStoreInfoRetriever()
    await navigate_to_page(page, get_full_lowes_url(STORE_LINKS[0]))
    store_info = await client.parse_store_page(page, store_id=TEST_STORES[0].store_id)
    assert str(TEST_STORES[0]) == str(store_info)


async def test_process_store_page(page: Page):
    client = StateStoreInfoRetriever()
    store_info = await client.process_store_page(
        page, store_link=STORE_LINKS[0], store_id=TEST_STORES[0].store_id
    )
    assert str(TEST_STORES[0]) == str(store_info)


@patch(
    "lowes.scripts.retrieve_store_info.StateStoreInfoRetriever.save_store_infos_for_state"
)
@patch(
    "lowes.scripts.retrieve_store_info.StateStoreInfoRetriever.process_store_page",
    # Use side_effect to return a list instead of a single value with "return_value"
    side_effect=TEST_STORES,
)
async def test_process_all_state_stores(
    mock_process_store_page: Mock,
    mock_save_store_infos_for_state: Mock,
    page: Page,
):
    client = StateStoreInfoRetriever()

    await client.process_all_state_stores(page, store_links=STORE_LINKS, state=STATE)

    # Assert that process_store_page was called for each store link
    for mock_call, store_link in zip(
        mock_process_store_page.call_args_list, STORE_LINKS
    ):
        assert mock_call.kwargs["store_link"] == store_link

    mock_save_store_infos_for_state.assert_called_once()

    store_info_list = mock_save_store_infos_for_state.call_args.args[0]
    for store, test_store in zip(store_info_list, TEST_STORES):
        assert str(store) == str(test_store)


@patch(
    "lowes.scripts.retrieve_store_info.StateStoreInfoRetriever.process_all_state_stores",
)
@patch(
    "lowes.scripts.retrieve_store_info.StateStoreInfoRetriever.get_state_store_links",
    return_value=STORE_LINKS,
)
async def test_get_store_infos_for_state(
    mock_get_state_store_links: Mock,
    mock_process_all_state_stores: Mock,
    context: BrowserContext,
):
    client = StateStoreInfoRetriever()
    await client.get_store_infos_for_state(
        context,
        state_link=STATE_LINK,
    )

    mock_get_state_store_links.assert_called_once()
    assert (
        mock_get_state_store_links.call_args_list[0].kwargs["state_link"] == STATE_LINK
    )
    assert mock_get_state_store_links.call_args_list[0].kwargs["state"] == STATE

    mock_process_all_state_stores.assert_called_once()
    assert (
        mock_process_all_state_stores.call_args_list[0].kwargs["store_links"]
        == STORE_LINKS
    )
    assert mock_process_all_state_stores.call_args_list[0].kwargs["state"] == STATE
