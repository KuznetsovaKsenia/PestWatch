from playwright.sync_api import (
    Page,
    expect,
)

from tests.e2e.pages import (
    AssessmentPage,
    HistoryPage,
)


def test_real_assessment_runs_through_browser_and_is_saved(
    page: Page,
    base_url: str,
):
    assessment_page = AssessmentPage(
        page,
        base_url,
    )

    history_page = HistoryPage(
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

    assessment_page.open()

    # Убеждаемся, что открыта обычная,
    # а не демонстрационная форма.
    expect(
        assessment_page.demo_banner
    ).to_be_hidden()

    expect(
        assessment_page.real_location_field
    ).to_be_visible()

    expect(
        assessment_page.demo_location_field
    ).to_be_hidden()

    assessment_page.fill_location(
        name="Калуга",
        region="Калужская область",
        country="Россия",
    )

    assessment_page.select_profile(
        "HUMAN"
    )

    # Ждём именно REAL endpoint.
    with page.expect_response(
        lambda response: (
            response.request.method == "POST"
            and response.url.endswith(
                "/api/assessments"
            )
        )
    ) as response_info:
        assessment_page.submit()

    response = response_info.value

    assert response.status == 201

    # Результат реально отрисован JavaScript.
    expect(
        assessment_page.result_section
    ).to_be_visible()

    expect(
        assessment_page.risk_cards
    ).to_have_count(1)

    expect(
        assessment_page.risk_results
    ).to_contain_text(
        "Клещи"
    )

    # Network contract:
    # обычная оценка не должна использовать
    # demo endpoint.
    real_posts = [
        url
        for url in assessment_posts
        if url.endswith(
            "/api/assessments"
        )
    ]

    demo_posts = [
        url
        for url in assessment_posts
        if url.endswith(
            "/api/assessments/demo"
        )
    ]

    assert len(real_posts) == 1
    assert demo_posts == []

    # Теперь проверяем persistence уже
    # через пользовательский интерфейс истории.
    history_page.open()

    expect(
        history_page.cards
    ).to_have_count(1)

    card = history_page.card_by_location(
        "Калуга"
    )

    expect(
        card
    ).to_be_visible()

    expect(
        card
    ).to_contain_text(
        "Калуга"
    )

    expect(
        card
    ).to_contain_text(
        "Калужская область"
    )

    expect(
        card
    ).to_contain_text(
        "Человек"
    )

    expect(
        card
    ).to_contain_text(
        "Обычная оценка"
    )


def test_real_assessment_details_and_history_detail(
    page: Page,
    base_url: str,
):
    assessment_page = AssessmentPage(
        page,
        base_url,
    )

    history_page = HistoryPage(
        page,
        base_url,
    )

    assessment_page.open()

    assessment_page.fill_location(
        name="Калуга",
        region="Калужская область",
        country="Россия",
    )

    assessment_page.select_profile(
        "HUMAN"
    )

    with page.expect_response(
        lambda response: (
            response.request.method == "POST"
            and response.url.endswith(
                "/api/assessments"
            )
        )
    ) as response_info:
        assessment_page.submit()

    response = response_info.value

    assert response.status == 201

    body = response.json()
    assessment_id = (
        body["data"]["id"]
    )

    assert assessment_id is not None

    # -------------------------------------------------
    # 1. Проверяем результат текущей REAL assessment.
    # -------------------------------------------------

    expect(
        assessment_page.result_section
    ).to_be_visible()

    expect(
        assessment_page.risk_results
    ).to_contain_text(
        "Клещи"
    )

    # -------------------------------------------------
    # 2. Открываем подробности результата.
    # -------------------------------------------------

    assessment_page.open_risk_details(
        "TICK"
    )

    expect(
        assessment_page.details_dialog
    ).to_be_visible()

    expect(
        assessment_page.details_dialog
    ).to_contain_text(
        "Клещи"
    )

    expect(
        assessment_page.details_level
    ).not_to_be_empty()

    expect(
        assessment_page.details_meaning
    ).to_be_visible()

    expect(
        assessment_page.details_meaning
    ).not_to_be_empty()

    expect(
        assessment_page.details_calculation
    ).to_be_visible()

    expect(
        assessment_page.details_calculation
    ).not_to_be_empty()

    expect(
        assessment_page.details_inputs
    ).to_be_visible()

    expect(
        assessment_page.details_inputs
    ).not_to_be_empty()

    expect(
        assessment_page.details_recommendations
    ).to_be_visible()

    expect(
        assessment_page.details_recommendations
    ).not_to_be_empty()

    expect(
        assessment_page.details_sources
    ).to_be_visible()

    expect(
        assessment_page.details_sources
    ).not_to_be_empty()

    # -------------------------------------------------
    # 3. Переходим в историю.
    # -------------------------------------------------

    history_page.open()

    card = history_page.card_by_location(
        "Калуга"
    )

    expect(card).to_be_visible()

    expect(
        card
    ).to_contain_text(
        "Человек"
    )

    expect(
        card
    ).to_contain_text(
        "Обычная оценка"
    )

    # -------------------------------------------------
    # 4. Открываем именно созданную assessment.
    # -------------------------------------------------

    history_page.open_assessment(
        assessment_id
    )

    expect(page).to_have_url(
        (
            f"{base_url}/history/"
            f"{assessment_id}"
        )
    )

    # -------------------------------------------------
    # 5. Проверяем persisted history detail.
    # -------------------------------------------------

    expect(
        page.locator(
            ".history-detail__header"
        )
    ).to_contain_text(
        "Калуга"
    )

    expect(
        page.locator(
            ".history-detail__header"
        )
    ).to_contain_text(
        "Человек"
    )

    expect(
        page.locator(
            ".history-risk-card"
        )
    ).to_have_count(1)

    expect(
        page.locator(
            ".history-risk-card"
        )
    ).to_contain_text(
        "Иксодовые клещи"
    )

    # Проверяем persisted evidence:
    # история должна содержать данные,
    # сохранённые при выполнении assessment.
    expect(
        page.locator(
            ".history-detail"
        )
    ).to_contain_text(
        "Факторы оценки"
    )

    expect(
        page.locator(
            ".history-detail"
        )
    ).to_contain_text(
        "Сохранённый снимок данных"
    )

    expect(
        page.locator(
            ".history-detail"
        )
    ).to_contain_text(
        "Температура воздуха"
    )

    expect(
        page.locator(
            ".history-detail"
        )
    ).to_contain_text(
        "Относительная влажность"
    )

    expect(
    page.locator(
        ".history-detail"
        )
    ).to_contain_text(
        "Дефицит влажности воздуха"
    )

    expect(
        page.locator(
            ".history-detail__note"
        )
    ).to_contain_text(
        "Исторический результат"
    )