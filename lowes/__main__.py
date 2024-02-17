from lowes.scripts.get_and_save_state_links import get_and_save_state_links
from lowes.utils.playwright import run_with_playwright

if __name__ == "__main__":
    run_with_playwright(get_and_save_state_links)
