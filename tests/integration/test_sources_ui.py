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


def test_dialog_contains_sources_target(client):
    response = client.get("/")

    assert response.status_code == 200
    assert (
        b'id="risk-details-sources"'
        in response.data
    )


def test_source_registry_contains_all_four_threats(client):
    text = script(client)

    assert "const riskSourceRegistry={" in text
    assert "TICK:[" in text
    assert "CABBAGE_APHID:[" in text
    assert "COLORADO_BEETLE:[" in text
    assert "CODLING_MOTH:[" in text


def test_source_registry_uses_supported_purpose_types(client):
    text = script(client)

    assert 'CALCULATION:"Для расчёта"' in text
    assert 'METHODOLOGY:"Методика расчёта"' in text
    assert 'RECOMMENDATION:"Для рекомендаций"' in text


def test_tick_sources_include_calculation_and_rospotrebnadzor(client):
    text = script(client)

    assert "PMC4311481" in text
    assert "Роспотребнадзор" in text
    assert "менее 5 мм рт. ст." in text


def test_cabbage_aphid_sources_support_temperature_and_recommendations(client):
    text = script(client)

    assert "PMC6303750" in text
    assert "15–25 °C" in text
    assert "Cabbage Aphid — Cole Crops" in text


def test_colorado_sources_include_11c_and_extension_guidance(client):
    text = script(client)

    assert "11 °C" in text
    assert "10.2903/j.efsa.2020.6359" in text
    assert "Colorado potato beetle" in text


def test_codling_moth_methodology_does_not_claim_130_is_source_validated(client):
    text = script(client)

    assert (
        "Не подтверждает конкретный порог PestWatch "
        "130 градусо-дней."
        in text
    )
    assert "Codling Moth — Phenology Models" in text
    assert "Codling Moth — Apple" in text


def test_source_links_open_safely_in_new_tab(client):
    text = script(client)

    assert 'target="_blank"' in text
    assert 'rel="noopener noreferrer"' in text
    assert "Открыть источник ↗" in text


def test_sources_are_bound_when_modal_opens(client):
    text = script(client)

    assert "function bindSources(result)" in text
    assert "bindSources(result);" in text
    assert (
        "riskDetailsSources.innerHTML=sourcesHtml(result)"
        in text
    )


def test_sources_slice_does_not_fetch_or_recalculate(client):
    text = script(client)
    slice_34c = text.split(
        "SLICE 3.4C-B — SOURCES UI",
        1,
    )[1]

    assert "fetch(" not in slice_34c
    assert "/api/" not in slice_34c
    assert "Math." not in slice_34c


def test_cabbage_aphid_recommendation_removes_unverified_wild_radish(client):
    text = script(client)

    assert "пастушью сумку" in text
    assert "дикую редьку" not in text


def test_source_styles_exist(client):
    text = client.get(
        "/static/css/styles.css"
    ).data.decode("utf-8")

    assert ".source-details" in text
    assert ".source-item" in text
    assert ".source-purpose--calculation" in text
    assert ".source-purpose--methodology" in text
    assert ".source-purpose--recommendation" in text
    assert ".source-link" in text
