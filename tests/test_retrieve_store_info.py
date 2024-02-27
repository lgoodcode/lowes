from os import path
from typing import List
from unittest.mock import Mock, mock_open, patch

from playwright.async_api import Page

from lowes.constants import STATE_STORES_LINKS_DIR
from lowes.scripts.retrieve_store_info import (
    StoreInfo,
    get_state_store_links,
    parse_store_page,
    process_all_state_stores,
    process_store_page,
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

LOWES_STORES: List[StoreInfo] = [StoreInfo(*data.split(",")) for data in STORE_DATA]


def test_lowes_stores():
    assert len(LOWES_STORES) == 4
    assert LOWES_STORES[0].store_id == "2525"
    assert LOWES_STORES[0].address == "235 Colonial Promenade Pkwy"
    assert LOWES_STORES[0].city == "Alabaster"
    assert LOWES_STORES[0].state == "AL"
    assert LOWES_STORES[0].zipcode == "35007"


async def test_parse_store_page(page: Page):
    await navigate_to_page(page, get_full_lowes_url(STORE_LINKS[0]))
    store_info = await parse_store_page(page, LOWES_STORES[0].store_id)
    assert str(LOWES_STORES[0]) == str(store_info)


@patch("builtins.open", new_callable=mock_open)
async def test_save_store_links(mock_open_arg: Mock):
    mock_store_links = STORE_LINKS
    mock_state = STATE

    save_store_links(mock_store_links, mock_state)

    mock_file_path = path.join(
        STATE_STORES_LINKS_DIR, f"{mock_state.lower()}_store_links.txt"
    )

    # Assert that the mocked file was opened with correct parameters
    mock_open_arg.assert_called_once_with(mock_file_path, "w", encoding="utf-8")
    handle = mock_open_arg()

    for link in mock_store_links:
        handle.write.assert_any_call(link + "\n")
    assert handle.write.call_count == len(mock_store_links)


@patch("lowes.scripts.retrieve_store_info.save_store_links")
@patch("lowes.scripts.retrieve_store_info.get_store_links", return_value=STORE_LINKS)
async def test_get_state_store_links(
    mock_get_store_links: Mock, mock_save_store_links: Mock, page: Page
):
    store_links = await get_state_store_links(page, STORE_LINKS[0], STATE)
    assert store_links == STORE_LINKS


async def test_process_store_page(page: Page):
    store_info = await process_store_page(page, STATE, STORE_LINKS[0])
    assert str(LOWES_STORES[0]) == str(store_info)


@patch("lowes.scripts.retrieve_store_info.save_store_infos_for_state")
@patch(
    "lowes.scripts.retrieve_store_info.process_store_page",
    # Use side_effect to return a list instead of a single value with "return_value"
    side_effect=LOWES_STORES,
)
async def test_process_all_state_stores(
    mock_process_store_page: Mock,
    mock_save_store_infos_for_state: Mock,
    page: Page,
):
    await process_all_state_stores(page, STORE_LINKS, STATE)

    for store_link in STORE_LINKS:
        mock_process_store_page.assert_any_call(page, STATE, store_link)

    mock_save_store_infos_for_state.assert_called_once()

    store_info_list = mock_save_store_infos_for_state.call_args.args[0]
    for store_info, lowes_store in zip(store_info_list, LOWES_STORES):
        assert str(store_info) == str(lowes_store)
