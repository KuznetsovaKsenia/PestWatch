import pytest

from app import create_app
from app.config.settings import TestConfig


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


def script(client):
    return client.get(
        "/static/js/assessment.js"
    ).data.decode("utf-8")


def test_dialog_contains_result_meaning_target(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b'id="risk-details-meaning"' in response.data


def test_result_meaning_supports_all_four_threats(client):
    text = script(client)

    assert "function tickResultMeaning" in text
    assert "function cabbageAphidResultMeaning" in text
    assert "function coloradoBeetleResultMeaning" in text
    assert "function codlingMothResultMeaning" in text


def test_result_meaning_uses_two_risk_semantic_groups(client):
    text = script(client)

    assert (
        '["ELEVATED","HIGH"].includes(result?.risk_level)'
        in text
    )


def test_tick_meaning_does_not_claim_presence(client):
    text = script(client)

    assert (
        "не подтверждённое наличие клещей в конкретном месте"
        in text
    )
    assert "не означает, что клещей рядом нет" in text


def test_cabbage_aphid_meaning_requires_observation_for_presence(client):
    text = script(client)

    assert (
        "PestWatch не определяет, есть ли тля "
        "на конкретных растениях"
        in text
    )
    assert (
        "не означает отсутствия тли на растениях"
        in text
    )


def test_colorado_meaning_preserves_possible_emergence_semantics(client):
    text = script(client)

    assert (
        "могут начинать выходить на поверхность"
        in text
    )
    assert (
        "не подтверждает, что жуки уже появились "
        "на ваших посадках"
        in text
    )


def test_codling_meaning_does_not_claim_actual_flight(client):
    text = script(client)

    assert (
        "периода возможной сезонной активности "
        "яблонной плодожорки"
        in text
    )
    assert (
        "не подтверждает фактический лёт плодожорки"
        in text
    )


def test_insufficient_data_meaning_does_not_equal_no_risk(client):
    text = script(client)

    assert (
        "Недостаток данных не означает отсутствия угрозы"
        in text
    )


def test_result_meaning_is_bound_when_modal_opens(client):
    text = script(client)

    assert "function bindResultMeaning(result)" in text
    assert "bindResultMeaning(result);" in text
    assert (
        "riskDetailsMeaning.innerHTML=resultMeaningHtml(result)"
        in text
    )


def test_result_meaning_slice_does_not_fetch_or_recalculate(client):
    text = script(client)
    slice_35 = text.split(
        "SLICE 3.5 — RESULT MEANING",
        1,
    )[1]

    assert "fetch(" not in slice_35
    assert "/api/" not in slice_35
    assert "Math." not in slice_35


def test_result_meaning_styles_exist(client):
    text = client.get(
        "/static/css/styles.css"
    ).data.decode("utf-8")

    assert ".result-meaning" in text
    assert ".result-meaning__summary" in text
    assert ".result-meaning__note" in text
