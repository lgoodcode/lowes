from unittest.mock import Mock, mock_open, patch

from playwright.async_api import BrowserContext, Page

from lowes.constants import DEPARTMENT_LINKS_PATH, LOWES_DEPARTMENTS_URL
from lowes.scripts.retrieve_department_links import DepartmentLinkRetriever
from lowes.utils.playwright import navigate_to_page

TEST_DEPT_LINKS = [
    "/pl/Accessible-bathroom-Accessible-home/37721669146437",
    "/pl/Accessible-bedroom-Accessible-home/4294644781",
    "/pl/Accessible-entry-home-Accessible-home/37721669146444",
    "/pl/Accessible-kitchen-Accessible-home/1111913019980",
]

NUM_DEPT_LINKS = 384  # This number is from the initial full run


async def test_lowes_get_department_links(page: Page):
    client = DepartmentLinkRetriever()
    await navigate_to_page(page, LOWES_DEPARTMENTS_URL)
    await client.get_links(page)
    assert len(client.links) == NUM_DEPT_LINKS


@patch("builtins.open", new_callable=mock_open)
def test_save_department_links(mock_open_arg: Mock):
    client = DepartmentLinkRetriever()
    client.links = TEST_DEPT_LINKS
    client.save_links()

    mock_open_arg.assert_called_once_with(DEPARTMENT_LINKS_PATH, "w", encoding="utf-8")
    handle = mock_open_arg()

    assert handle.write.call_args_list[0].args[0] == "".join(TEST_DEPT_LINKS) + "\n"
    assert handle.write.call_count == 1


@patch("builtins.open", new_callable=mock_open)
async def test_main(mock_open_arg: Mock, context: BrowserContext):
    client = DepartmentLinkRetriever()
    await client.main(1)
    mock_open_arg.assert_called_once_with(DEPARTMENT_LINKS_PATH, "w", encoding="utf-8")
    handle = mock_open_arg()
    assert handle.write.call_count == 1
    assert len(client.links) == NUM_DEPT_LINKS
