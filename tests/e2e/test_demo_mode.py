from playwright.sync_api import (
    Page,
    expect,
)

from tests.e2e.pages import AssessmentPage


def test_demo_assessment_runs_through_browser(
    page: Page,
    base_url: str,
):
    assessment_page = AssessmentPage(
        page,
        base_url,
    )

    assessment_posts = []

    def capture_request(request):
        if (
            request.method == "POST"
            and "/api/assessments" in request.url
        ):
            assessment_posts.append(
                request.url
            )

    page.on(
        "request",
        capture_request,
    )

    # Пользователь входит в Demo Mode
    # через каталог угроз.
    page.goto(
        f"{base_url}/threats",
        wait_until="networkidle",
    )

    page.get_by_role(
        "link",
        name="Демонстрационный режим",
    ).click()

    expect(page).to_have_url(
        f"{base_url}/?demo=1"
    )

    expect(
        assessment_page.demo_banner
    ).to_be_visible()

    expect(
        assessment_page.demo_location_field
    ).to_be_visible()

    expect(
        assessment_page.real_location_field
    ).to_be_hidden()

    # DEMO_C = Омск.
    assessment_page.select_demo_location(
        "DEMO_C"
    )

    expect(
        assessment_page.location_region
    ).to_have_value(
        "Омская область"
    )

    expect(
        assessment_page.location_country
    ).to_have_value(
        "Россия"
    )

    assessment_page.select_profile(
        "GARDEN"
    )

    # Ждём именно demo endpoint.
    with page.expect_response(
        lambda response: (
            response.request.method == "POST"
            and response.url.endswith(
                "/api/assessments/demo"
            )
        )
    ) as response_info:
        assessment_page.submit()

    response = response_info.value

    assert response.status == 201

    expect(
        assessment_page.result_section
    ).to_be_visible()

    expect(
        assessment_page.risk_cards
    ).to_have_count(1)

    expect(
        assessment_page.risk_results
    ).to_contain_text(
        "Яблонная плодожорка"
    )

    # Критичный network contract:
    # Demo Mode не должен отправлять
    # обычную REAL assessment.
    demo_posts = [
        url
        for url in assessment_posts
        if url.endswith(
            "/api/assessments/demo"
        )
    ]

    real_posts = [
        url
        for url in assessment_posts
        if url.endswith(
            "/api/assessments"
        )
    ]

    assert len(demo_posts) == 1
    assert real_posts == []

def test_demo_mode_persists_during_navigation_and_exits_explicitly(
    page: Page,
    base_url: str,
):
    assessment_page = AssessmentPage(
        page,
        base_url,
    )

    # Входим в Demo Mode через каталог угроз.
    page.goto(
        f"{base_url}/threats",
        wait_until="networkidle",
    )

    page.get_by_role(
        "link",
        name="Демонстрационный режим",
    ).click()

    expect(page).to_have_url(
        f"{base_url}/?demo=1"
    )

    expect(
        assessment_page.demo_banner
    ).to_be_visible()

    expect(
        assessment_page.demo_location_field
    ).to_be_visible()

    expect(
        assessment_page.real_location_field
    ).to_be_hidden()

    # Переходим в историю.
    page.get_by_role(
        "link",
        name="История",
    ).click()

    expect(page).to_have_url(
        f"{base_url}/history"
    )

    # Возвращаемся на страницу оценки
    # обычной навигационной ссылкой.
    page.get_by_role(
        "link",
        name="Оценка риска",
    ).click()

    expect(page).to_have_url(
        f"{base_url}/?demo=1"
    )

    # Demo Mode должен сохраниться.
    expect(
        assessment_page.demo_banner
    ).to_be_visible()

    expect(
        assessment_page.demo_location_field
    ).to_be_visible()

    expect(
        assessment_page.real_location_field
    ).to_be_hidden()

    # Выходим только явным действием пользователя.
    assessment_page.exit_demo_mode()

    expect(page).to_have_url(
        f"{base_url}/"
    )

    # После явного выхода должна восстановиться
    # обычная форма оценки.
    expect(
        assessment_page.demo_banner
    ).to_be_hidden()

    expect(
        assessment_page.demo_location_field
    ).to_be_hidden()

    expect(
        assessment_page.real_location_field
    ).to_be_visible()

    # Проверяем, что состояние действительно очищено:
    # History -> Assessment больше не возвращает Demo.
    page.get_by_role(
        "link",
        name="История",
    ).click()

    expect(page).to_have_url(
        f"{base_url}/history"
    )

    page.get_by_role(
        "link",
        name="Оценка риска",
    ).click()

    expect(page).to_have_url(
        f"{base_url}/"
    )

    expect(
        assessment_page.demo_banner
    ).to_be_hidden()

    expect(
        assessment_page.real_location_field
    ).to_be_visible()    

def test_demo_result_details_are_available(
    page: Page,
    base_url: str,
):
    assessment_page = AssessmentPage(
        page,
        base_url,
    )

    assessment_page.open_demo()

    expect(
        assessment_page.demo_banner
    ).to_be_visible()

    # DEMO_C + GARDEN даёт один
    # детерминированный результат:
    # яблонная плодожорка.
    assessment_page.select_demo_location(
        "DEMO_C"
    )

    assessment_page.select_profile(
        "GARDEN"
    )

    with page.expect_response(
        lambda response: (
            response.request.method == "POST"
            and response.url.endswith(
                "/api/assessments/demo"
            )
        )
    ) as response_info:
        assessment_page.submit()

    assert (
        response_info.value.status
        == 201
    )

    expect(
        assessment_page.result_section
    ).to_be_visible()

    expect(
        assessment_page.risk_cards
    ).to_have_count(1)

    expect(
        assessment_page.risk_results
    ).to_contain_text(
        "Яблонная плодожорка"
    )

    # Открываем подробности именно
    # сохранённого RiskResult из ответа.
    assessment_page.open_risk_details(
        "CODLING_MOTH"
    )

    expect(
        assessment_page.details_dialog
    ).to_be_visible()

    # Проверяем identity / risk level.
    expect(
        assessment_page.details_dialog
    ).to_contain_text(
        "Яблонная плодожорка"
    )

    expect(
        assessment_page.details_level
    ).not_to_be_empty()

    # Смысл результата.
    expect(
        assessment_page.details_meaning
    ).to_be_visible()

    expect(
        assessment_page.details_meaning
    ).not_to_be_empty()

    # Расчёт и факторы.
    expect(
        assessment_page.details_calculation
    ).to_be_visible()

    expect(
        assessment_page.details_calculation
    ).not_to_be_empty()

    # Сохранённые/использованные
    # исходные данные.
    expect(
        assessment_page.details_inputs
    ).to_be_visible()

    expect(
        assessment_page.details_inputs
    ).not_to_be_empty()

    # Рекомендации.
    expect(
        assessment_page.details_recommendations
    ).to_be_visible()

    expect(
        assessment_page.details_recommendations
    ).not_to_be_empty()

    # Источники.
    expect(
        assessment_page.details_sources
    ).to_be_visible()

    expect(
        assessment_page.details_sources
    ).not_to_be_empty()