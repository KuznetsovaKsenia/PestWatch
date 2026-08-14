from playwright.sync_api import (
    Locator,
    Page,
)


class AssessmentPage:
    def __init__(
        self,
        page: Page,
        base_url: str,
    ):
        self.page = page
        self.base_url = base_url

    @property
    def form(self) -> Locator:
        return self.page.locator(
            "#assessment-form"
        )

    @property
    def submit_button(self) -> Locator:
        return self.page.locator(
            "#assessment-submit"
        )

    @property
    def error_message(self) -> Locator:
        return self.page.locator(
            "#assessment-error"
        )

    @property
    def result_section(self) -> Locator:
        return self.page.locator(
            "#assessment-result"
        )

    @property
    def risk_results(self) -> Locator:
        return self.page.locator(
            "#risk-results"
        )

    @property
    def demo_banner(self) -> Locator:
        return self.page.locator(
            "#demo-mode-banner"
        )

    @property
    def demo_exit(self) -> Locator:
        return self.page.locator(
            "#demo-mode-exit"
        )

    @property
    def real_location_field(self) -> Locator:
        return self.page.locator(
            "#real-location-field"
        )

    @property
    def demo_location_field(self) -> Locator:
        return self.page.locator(
            "#demo-location-field"
        )

    @property
    def location_name(self) -> Locator:
        return self.page.locator(
            "#location-name"
        )

    @property
    def location_region(self) -> Locator:
        return self.page.locator(
            "#location-region"
        )

    @property
    def location_country(self) -> Locator:
        return self.page.locator(
            "#location-country"
        )

    @property
    def demo_location_select(self) -> Locator:
        return self.page.locator(
            "#demo-location-select"
        )

    @property
    def risk_cards(self) -> Locator:
        return self.page.locator(
            ".risk-card"
        )

    @property
    def details_dialog(self) -> Locator:
        return self.page.locator(
            "#risk-details-dialog"
        )

    @property
    def details_level(self) -> Locator:
        return self.page.locator(
            "#risk-details-level"
        )

    @property
    def details_meaning(self) -> Locator:
        return self.page.locator(
            "#risk-details-meaning"
        )

    @property
    def details_recommendations(
        self,
    ) -> Locator:
        return self.page.locator(
            "#risk-details-recommendations"
        )

    @property
    def details_calculation(
        self,
    ) -> Locator:
        return self.page.locator(
            "#risk-details-calculation"
        )

    @property
    def details_inputs(self) -> Locator:
        return self.page.locator(
            "#risk-details-inputs"
        )

    @property
    def details_sources(self) -> Locator:
        return self.page.locator(
            "#risk-details-sources"
        )

    def open(self):
        return self.page.goto(
            self.base_url,
            wait_until="networkidle",
        )

    def open_demo(self):
        return self.page.goto(
            f"{self.base_url}/?demo=1",
            wait_until="networkidle",
        )

    def fill_location(
        self,
        *,
        name: str,
        region: str,
        country: str = "Россия",
    ):
        self.location_name.fill(name)
        self.location_region.fill(region)
        self.location_country.fill(country)

    def select_demo_location(
        self,
        scenario_id: str,
    ):
        self.demo_location_select.select_option(
            scenario_id
        )

    def select_profile(
        self,
        profile: str,
    ):
        self.page.locator(
            f'input[name="profile"][value="{profile}"]'
        ).check()

    def submit(self):
        self.submit_button.click()

    def open_risk_details(
        self,
        threat_code: str,
    ):
        self.page.locator(
            ".risk-details-trigger"
            f'[data-threat-code="{threat_code}"]'
        ).click()

    def exit_demo_mode(self):
        self.demo_exit.click()