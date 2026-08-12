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


def test_temperature_formatter_preserves_significant_decimal(client):
    text = script(client)

    assert "function temperatureValue(v)" in text
    assert "Number.isInteger(n)?String(n)" in text
    assert 'n.toFixed(1).replace(".",",")' in text


def test_weather_summary_does_not_round_air_temperature_to_integer(client):
    text = script(client)

    assert (
        "const temperature=temperatureValue(w.temperature)"
        in text
    )
    assert (
        "const temperature=round(w.temperature)"
        not in text
    )


def test_factor_cards_use_same_temperature_formatter(client):
    text = script(client)

    assert (
        "function factorView(f,threatCode,a)"
        "{const v=temperatureValue(f.actual_value);"
        in text
    )


def test_calculation_details_use_consistent_temperature_formatter(client):
    text = script(client)

    assert (
        "`${temperatureValue(temperature.actual_value)} °C`"
        in text
    )
    assert (
        "`${temperatureValue(sourceTemperatures[index])} °C`"
        in text
    )
    assert (
        "`${temperatureValue(factor.actual_value)} °C`"
        in text
    )
    assert (
        "`${temperatureValue(degreeDays.base_temperature)} °C`"
        in text
    )


def test_fix_c_keeps_fix_a_user_facing_humidity_wording(client):
    text = script(client)
    slice_33 = text.split(
        "SLICE 3.3 — CALCULATION DETAILS",
        1,
    )[1]

    assert "Не участвует в текущей модели" not in slice_33
    assert "Не влияет на текущую оценку риска" in slice_33
