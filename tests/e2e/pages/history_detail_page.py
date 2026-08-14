from playwright.sync_api import (
    Locator,
    Page,
)


class HistoryDetailPage:
    def __init__(
        self,
        page: Page,
        base_url: str,
    ):
        self.page = page
        self.base_url = base_url

    @property
    def header(self) -> Locator:
        return self.page.locator(
            ".history-detail__header"
        )

    @property
    def risk_cards(self) -> Locator:
        return self.page.locator(
            ".history-risk-card"
        )

    @property
    def snapshot(self) -> Locator:
        return self.page.locator(
            ".history-snapshot"
        )

    @property
    def historical_note(self) -> Locator:
        return self.page.locator(
            ".history-detail__note"
        )

    @property
    def back_link(self) -> Locator:
        return self.page.locator(
            ".history-detail__back a"
        )

    def open(
        self,
        assessment_id: int,
    ):
        return self.page.goto(
            (
                f"{self.base_url}/history/"
                f"{assessment_id}"
            ),
            wait_until="networkidle",
        )

    def back_to_history(self):
        self.back_link.click()