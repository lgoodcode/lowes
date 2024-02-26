# type: ignore

import asyncio
import functools
from typing import Any

from lowes.utils.logger import get_logger

logger = get_logger()


def retry(tries: int = 3, delay: int = 1, backoff: int = 1):
    """Retries a function a number of times with a delay and backoff.

    Args:
        tries: The number of retries to attempt. Defaults to 3.
        delay: The time in seconds between each retry. Defaults to 1.
        backoff: Multiplier applied to the delay. Defaults to 1.
    """

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            retries = 0

            while retries < tries:
                try:
                    result = await func(*args, **kwargs)
                    return result

                except Exception as e:
                    logger.warning(f"[RETRYING]: {e}")
                    retries += 1
                    await asyncio.sleep(delay * backoff)

                    if not retries < tries:
                        raise Exception(f"[RETRIES EXHAUSTED]: {e}")

        return wrapper

    return decorator
