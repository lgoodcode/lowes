from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Coroutine, List

from playwright.async_api import Playwright, async_playwright

from lowes.utils.logger import get_logger
from lowes.utils.tasks import batch_tasks


class TaskRunner(ABC):
    __name: str
    logger: Logger
    tasks: List[Coroutine[Any, Any, None]]

    def __init__(self) -> None:
        self.__name = self.__class__.__name__
        self.logger = get_logger()
        self.tasks = []

    @property
    def name(self) -> str:
        return self.__name

    @abstractmethod
    async def create_tasks(self, playwright: Playwright, max_contexts: int): ...

    async def main(self, max_concurrency: int) -> None:
        async with async_playwright() as playwright:
            await self.create_tasks(playwright, max_concurrency)

            if len(self.tasks) == 0:
                raise Exception("No tasks to run")

            await batch_tasks(self.tasks)
