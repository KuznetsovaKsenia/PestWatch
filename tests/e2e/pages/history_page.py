from playwright.sync_api import (
    Locator,
    Page,
)


class HistoryPage:
    def __init__(
        self,
        page: Page,
        base_url: str,
    ):
        self.page = page
        self.base_url = base_url

    @property
    def cards(self) -> Locator:
        return self.page.locator(
            ".history-card"
        )

    @property
    def empty_state(self) -> Locator:
        return self.page.locator(
            ".history-empty"
        )

    def open(self):
        return self.page.goto(
            f"{self.base_url}/history",
            wait_until="networkidle",
        )

    def card_by_location(
        self,
        location_name: str,
    ) -> Locator:
        return self.cards.filter(
            has_text=location_name
        )

    def open_assessment(
        self,
        assessment_id: int,
    ):
        self.page.locator(
            f'a[href="/history/{assessment_id}"]'
        ).click()