from playwright.sync_api import Page, Playwright

from utils.playwright import get_page, navigate_to_page, run_playwright
from utils.utils import get_output_path

STATES_LIST_URL = "https://www.lowes.com/Lowes-Stores"
STATE_LINK_QUERY = "div[data-selector='str-storeDetailContainer'] .backyard.link"


def get_state_links(page: Page) -> list[str]:
    print("Getting state links")
    raw_state_link_els = page.query_selector_all(STATE_LINK_QUERY)
    # Skip the first two links, they are not states
    state_link_els = raw_state_link_els[2:]
    state_links: list[str] = []

    for state_link_el in state_link_els:
        if href := state_link_el.get_attribute("href"):
            state_links.append(href)
    return state_links


def save_state_links(state_links: list[str]) -> None:
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
