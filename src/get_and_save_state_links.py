from typing import List

from playwright.sync_api import Page, Playwright, sync_playwright

from utils.utils import get_output_path, get_page, navigate_to_page, run_playwright

STATES_LIST_URL = "https://www.lowes.com/Lowes-Stores"
STATE_LINK_QUERY = "div[data-selector='str-storeDetailContainer'] .backyard.link"


def get_state_links(page: Page) -> List[str]:
    print("Getting state links")
    raw_state_link_els = page.query_selector_all(STATE_LINK_QUERY)
    # Skip the first two links, they are not states
    state_link_els = raw_state_link_els[2:]
    state_links = [el.get_attribute("href") for el in state_link_els]
    return state_links


def save_state_links(state_links: List[str]) -> None:
    print("Saving state links")
    with open(get_output_path("state_links.txt"), "w", encoding="utf-8") as file:
        for state_link in state_links:
            file.write(state_link + "\n")


def runner(playwright: Playwright) -> None:
    page = get_page(playwright)

    try:
        print("Starting")
        navigate_to_page(page, STATES_LIST_URL)
        state_links = get_state_links(page)
        save_state_links(state_links)
        print("Done!")

    except Exception as e:
        print(f"Error while processing the page - {e}")

    finally:
        page.close()


def main():
    run_playwright(runner)


if __name__ == "__main__":
    main()
