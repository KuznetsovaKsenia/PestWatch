import pytest

from app import create_app
from app.config.settings import TestConfig


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


def test_dialog_contains_calculation_details_target(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'id="risk-details-calculation"' in response.data


def test_calculation_details_support_all_four_threats(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    assert 'result.threat_code==="TICK"' in text
    assert 'result.threat_code==="CABBAGE_APHID"' in text
    assert 'result.threat_code==="COLORADO_BEETLE"' in text
    assert 'result.threat_code==="CODLING_MOTH"' in text


def test_tick_details_use_persisted_factor_and_weather_values(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    assert 'findFactor(result,"SATURATION_DEFICIT")' in text
    assert "saturation?.actual_value" in text
    assert "w?.humidity" in text
    assert "менее 5 мм рт. ст." in text


def test_colorado_details_use_persisted_soil_estimate(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    assert "assessment?.input_snapshot?.soil_temperature_10cm_estimate" in text
    assert "source_depths_cm" in text
    assert "source_temperatures" in text
    assert "LINEAR_INTERPOLATION" in text


def test_codling_moth_details_use_persisted_degree_days(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    assert "assessment?.input_snapshot?.degree_days_10c" in text
    assert "degreeDays?.base_temperature" in text
    assert "degreeDays?.total" in text
    assert "130 градусо-дней" in text


def test_calculation_details_slice_does_not_fetch_or_recalculate(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    slice_33 = text.split("SLICE 3.3 — CALCULATION DETAILS", 1)[1]
    assert "fetch(" not in slice_33
    assert "/api/" not in slice_33
    assert "Math." not in slice_33
