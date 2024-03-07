from typing import Any, List

from playwright.async_api import Page

from lowes.constants import DEPARTMENT_LINKS_PATH, LOWES_DEPARTMENTS_URL
from lowes.utils.classes import TaskRunner
from lowes.utils.playwright import create_page, navigate_to_page

DEPARTMENT_SELECTOR = ".departments-container li.kuxg6u_engage-common-3.foDBid a"


class DepartmentLinkRetriever(TaskRunner):
    links: List[str]

    def __init__(self):
        super().__init__()
        self.links = []

    async def get_links(self, page: Page):
        self.logger.info("Getting department links")

        dept_link_els = await page.query_selector_all(DEPARTMENT_SELECTOR)
        links: List[str] = []

        for el in dept_link_els:
            if href := await el.get_attribute("href"):
                self.links.append(href)
        return links

    def save_links(self):
        self.logger.info("Saving department links")

        if len(self.links) == 0:
            raise Exception("No links to save")

        with open(DEPARTMENT_LINKS_PATH, "w", encoding="utf-8") as file:
            file.write("".join([link + "\n" for link in self.links]))

    async def task(
        self,
        page: Page,
    ) -> None:
        await navigate_to_page(page, LOWES_DEPARTMENTS_URL)
        await self.get_links(page)
        self.save_links()

    async def create_tasks(self, playwright: Any, max_contexts: int):
        self.tasks.append(self.task(await create_page(playwright)))
