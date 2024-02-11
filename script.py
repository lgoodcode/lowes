# from typing import List
# from playwright.sync_api import Playwright, sync_playwright, Page, ElementHandle

# CHROMIUM_KWARGS = {
#     "headless": False,
#     "channel": "chrome",
#     "args": [
#         "--disable-http2",
#         "--no-sandbox",
#     ],
# }

# STATES_LIST_URL = "https://www.lowes.com/Lowes-Stores"

# STATE_LINK_QUERY = "div[data-selector='str-storeDetailContainer'] .backyard.link"

# # STORE_ID_SELECTOR = "span.storeNo2"


# def navigate_to_store(page: Page, store_url: str) -> None:
#     print(f"Navigating to {store_url}")
#     page.goto(store_url, wait_until="domcontentloaded")
#     print(f"Arrived at {page.url}")


# def get_state_links(page: Page) -> List[str]:
#     raw_store_link_els = page.query_selector_all(STATE_LINK_QUERY)
#     # Skip the first two links, they are not states
#     store_link_els = raw_store_link_els[2:]
#     store_links = [el.get_attribute("href") for el in store_link_els]
#     return store_links


# # def get_el(page: Page, selector: str) -> ElementHandle:
# #     try:
# #         el = page.wait_for_selector(selector, timeout=3000)
# #         return el
# #     except Exception as e:
# #         raise Exception(f"Could not find selector {selector} - {e}") from e


# # def get_store_id(page: Page) -> str:
# #     store_id_el = get_el(page, STORE_ID_SELECTOR)
# #     raw_store_id_text = store_id_el.inner_text()
# #     store_id = raw_store_id_text.split("#")[1]
# #     return store_id


# def get_store(row_idx: int, item_idx: int) -> str:
#     return f"#mainContent > div > div.sc-jRQBWg.kmAmHd > div.GridStyles__GridRow-sc-1ejksnu-1.kCxbMF.row > div:nth-child({row_idx}) > div:nth-child({item_idx}) > a"


# # def get_item_data(page: Page, base_url: str) -> None:
# #     for row in range(1, 5):  # Rows 1 to 4
# #         for item in range(1, 9):  # Items 1 to 8 in each row
# #             try:
# #                 # Ensure the item is present and visible, increase timeout if necessary
# #                 if page.is_visible(get_store(row, item), timeout=10000):
# #                     page.click(item_selector)
# #                     page.wait_for_load_state("networkidle", timeout=10000)

# #                     info_selector = "#InfoBarCard > div > div.buttonsWrapper > div.titleMainWrapper > span"
# #                     if page.is_visible(info_selector, timeout=10000):
# #                         info_data = page.text_content(info_selector)
# #                         print(f"Data from row {row}, item {item}: {info_data}")
# #                     else:
# #                         print(f"Info not found for item at row {row}, column {item}")

# #                     page.goto(base_url, wait_until="domcontentloaded", timeout=10000)
# #                 else:
# #                     print(
# #                         f"Item at row {row}, column {item} is not visible or not found."
# #                     )
# #             except Exception as e:
# #                 print(f"Could not access item at row {row}, column {item}: {e}")
# #                 # Attempt to go back if an error occurs during navigation or data extraction
# #                 page.goto(base_url, wait_until="domcontentloaded", timeout=10000)

# def get_and_save_state_links(page: Page) -> None:
# 	print("Getting state links")
# 	state_links = get_state_links(page)

# 	with open("state_links.txt", "w") as file:
# 		for state_link in state_links:
# 			file.write(state_link + "\n")


# def main(playwright: Playwright) -> None:
#     browser = playwright.chromium.launch(**CHROMIUM_KWARGS)
#     context = browser.new_context()
#     page = context.new_page()

#     try:
#         # navigate_to_store(page, STORE_URL)
#         # get_item_data(page, STORE_URL)

#     except Exception as e:
#         print(f"Error while processing the page - {e}")

#     finally:
#         browser.close()


# with sync_playwright() as p:
#     main(p)
