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
    return client.get("/static/js/assessment.js").data.decode("utf-8")

def test_dialog_contains_input_data_target(client):
    assert b'id="risk-details-inputs"' in client.get("/").data

def test_input_data_summary_supports_all_four_threats(client):
    text=script(client)
    assert "function tickInputDataSummary" in text
    assert "function cabbageAphidInputDataSummary" in text
    assert "function coloradoBeetleInputDataSummary" in text
    assert "function codlingMothInputDataSummary" in text

def test_tick_input_summary_uses_current_weather(client):
    text=script(client)
    assert "Температура воздуха" in text
    assert "Относительная влажность" in text
    assert "Время наблюдения" in text

def test_cabbage_aphid_marks_humidity_as_reference_only(client):
    text=script(client)
    assert "Используется в оценке" in text
    assert "Показывается справочно" in text
    assert "уровень риска определяется температурой воздуха" in text

def test_colorado_input_summary_uses_persisted_source_soil_values(client):
    text=script(client)
    assert "soil_temperature_10cm_estimate" in text
    assert "source_depths_cm" in text
    assert "source_temperatures" in text
    assert "Исходные данные о почве" in text

def test_codling_moth_input_summary_uses_historical_observations(client):
    text=script(client)
    assert "degree_days_10c" in text
    assert "degreeDays?.observations" in text
    assert "degreeDays?.period_start" in text
    assert "degreeDays?.period_end" in text
    assert "historical_start_date" in text

def test_input_data_summary_is_bound_when_modal_opens(client):
    text=script(client)
    assert "function bindInputDataSummary(result)" in text
    assert "bindInputDataSummary(result);" in text
    assert "riskDetailsInputs.innerHTML=inputDataSummaryHtml" in text

def test_input_data_slice_does_not_fetch_or_recalculate(client):
    slice_36=script(client).split("SLICE 3.6 — INPUT DATA SUMMARY",1)[1]
    assert "fetch(" not in slice_36
    assert "/api/" not in slice_36
    assert "Math." not in slice_36

def test_input_data_summary_does_not_duplicate_risk_level(client):
    slice_36=script(client).split("SLICE 3.6 — INPUT DATA SUMMARY",1)[1]
    assert "Уровень риска" not in slice_36
    assert "risk_level" not in slice_36

def test_input_data_styles_exist(client):
    text=client.get("/static/css/styles.css").data.decode("utf-8")
    assert ".input-data-summary" in text
    assert ".input-data-block" in text
    assert ".input-data-row" in text
    assert ".input-data-block__note" in text
