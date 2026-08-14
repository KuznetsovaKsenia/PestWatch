from playwright.sync_api import (
    Page,
    expect,
)

from tests.e2e.pages import AssessmentPage


def test_home_page_opens_in_browser(
    page: Page,
    base_url: str,
):
    assessment_page = AssessmentPage(
        page,
        base_url,
    )

    response = assessment_page.open()

    assert response is not None
    assert response.ok

    expect(page).to_have_title(
        "PestWatch - Оценка риска вредных насекомых"
    )

    expect(
        page.get_by_role(
            "link",
            name="PestWatch",
        )
    ).to_be_visible()

    expect(
        assessment_page.form
    ).to_be_visible()

    expect(
        assessment_page.submit_button
    ).to_be_visible()