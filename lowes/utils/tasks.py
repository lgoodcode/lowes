from asyncio import Semaphore, gather
from typing import Any, Coroutine, List


async def custom_task(sem: Semaphore, task: Coroutine[Any, Any, None]):
    async with sem:
        await task


async def batch_tasks(
    tasks: List[Coroutine[Any, Any, None]],
    max_concurrency: int,
):
    sem = Semaphore(max_concurrency)
    async_tasks = [custom_task(sem, task) for task in tasks]
    await gather(*async_tasks)
