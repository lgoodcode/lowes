import argparse
from typing import Callable

from playwright.sync_api import Playwright

from lowes.scripts.get_and_save_state_links import get_and_save_state_links
from lowes.scripts.get_and_save_state_store_ids import get_and_save_state_store_ids
from lowes.utils.playwright import run_with_playwright

SCRIPTS: list[Callable[[Playwright], None]] = [
    get_and_save_state_links,
    get_and_save_state_store_ids,
]

parser = argparse.ArgumentParser(description="Run Lowe's scripts")
parser.add_argument(
    "script_number",
    type=str,
    choices=[i for i in range(len(SCRIPTS))],
    help="Choose the script to run:\n"
    + "\n".join(f"{script.__name__}\n" for script in SCRIPTS),
)

args = parser.parse_args()

# Run the selected script with Playwright
if __name__ == "__main__":
    script_number = args.script_number
    if not script_number:
        print("Please provide a script number")
        exit(1)

    try:
        script_number = int(script_number)

    except ValueError:
        print("Invalid script number: must be an integer")
        exit(1)

    selected_script = SCRIPTS[script_number]
    run_with_playwright(selected_script)
