import argparse
import asyncio
from typing import Any, List, Tuple

from lowes.scripts.async_get_and_save_state_links import async_get_and_save_state_links
from lowes.scripts.async_get_and_save_state_store_ids import (
    async_get_and_save_state_store_ids,
)
from lowes.scripts.get_and_save_state_links import get_and_save_state_links
from lowes.scripts.get_and_save_state_store_ids import get_and_save_state_store_ids
from lowes.utils.async_playwright import async_run_with_playwright
from lowes.utils.logger import get_logger
from lowes.utils.playwright import run_with_playwright

logger = get_logger()

SCRIPTS: List[Tuple[Any, bool]] = [
    (get_and_save_state_links, False),
    (get_and_save_state_store_ids, False),
    (async_get_and_save_state_links, True),
    (async_get_and_save_state_store_ids, True),
]


async def main():
    parser = argparse.ArgumentParser(description="Run Lowe's scripts")
    parser.add_argument(
        "script_number",
        type=int,
        choices=[i for i in range(len(SCRIPTS))],
        help="Choose the script to run:\n"
        + "\n".join(f"{script.__name__}\n" for script, _ in SCRIPTS),
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=2,
        help="Set the maximum number of concurrent tasks (default: 2).\nNote: only used for async scripts.",
    )

    args = parser.parse_args()
    script_number = int(args.script_number)
    max_concurrency = int(args.concurrency)
    selected_script, is_async = SCRIPTS[script_number]

    logger.info(f"[selected_script]: {selected_script.__name__}")
    logger.info(f"[max_concurrency]: {max_concurrency}")

    if is_async:
        await async_run_with_playwright(selected_script, max_concurrency)
    else:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_with_playwright, selected_script)


# Run the selected script with Playwright
if __name__ == "__main__":
    asyncio.run(main())
