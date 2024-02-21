import argparse
import asyncio
import traceback
from time import time
from typing import Any, List

from lowes.scripts.async_get_and_save_state_links import async_get_and_save_state_links
from lowes.scripts.async_get_and_save_state_store_info import (
    async_get_and_save_state_store_info,
)
from lowes.utils.async_playwright import async_run_with_context
from lowes.utils.logger import get_logger

logger = get_logger()

MAX_CONCURRENCY = 8
SCRIPTS: List[Any] = [
    async_get_and_save_state_links,
    async_get_and_save_state_store_info,
]


async def main():
    parser = argparse.ArgumentParser(description="Run Lowe's scripts")
    parser.add_argument(
        "script_number",
        type=int,
        choices=[i for i in range(len(SCRIPTS))],
        help="Choose the script to run:\n"
        + "\n".join(f"{script.__name__}\n" for script in SCRIPTS),
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=2,
        help="Set the maximum number of concurrent tasks (default: 2, max: 8).\nNote: only used for async scripts.",
    )

    args = parser.parse_args()
    script_number = int(args.script_number)
    max_concurrency = min(int(args.concurrency), MAX_CONCURRENCY)
    selected_script = SCRIPTS[script_number]

    start_time = time()
    logger.info(f"[selected_script]: {selected_script.__name__}")
    logger.info(f"[max_concurrency]: {max_concurrency}")

    try:
        await async_run_with_context(selected_script, max_concurrency)
        logger.info(f"{selected_script.__name__} completed successfully")
        logger.info(f"Time taken: {time() - start_time:.2f} seconds")

    except Exception as e:
        error_message = f"{e}\n{traceback.format_exc()}"
        logger.error(error_message)


# Run the selected script with Playwright
if __name__ == "__main__":
    asyncio.run(main())
