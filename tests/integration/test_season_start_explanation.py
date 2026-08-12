import pytest

from app import create_app
from app.config.settings import TestConfig


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


def test_codling_moth_season_start_rule_is_explained(client):
    text = client.get(
        "/static/js/assessment.js"
    ).data.decode("utf-8")

    assert 'detailRow("Начало сезона"' in text
    assert (
        'detailRow("Как определено",'
        '"3 дня подряд со средней температурой выше 10 °C")'
        in text
    )


def test_codling_moth_season_start_explanation_matches_detector_rule(
    client,
):
    text = client.get(
        "/static/js/assessment.js"
    ).data.decode("utf-8")

    assert (
        "первый день первых трёх последовательных дней "
        "со средней суточной температурой выше 10 °C"
        in text
    )

    assert (
        "С этой даты начинается накопление "
        "эффективных температур."
        in text
    )


def test_old_automatic_only_wording_is_removed(client):
    text = client.get(
        "/static/js/assessment.js"
    ).data.decode("utf-8")

    slice_33 = text.split(
        "SLICE 3.3 — CALCULATION DETAILS",
        1,
    )[1]

    assert (
        'detailRow("Начало определено автоматически"'
        not in slice_33
    )
