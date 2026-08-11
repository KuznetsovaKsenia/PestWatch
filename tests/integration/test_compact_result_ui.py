import pytest
from app import create_app
from app.config.settings import TestConfig

@pytest.fixture
def client():
    return create_app(TestConfig).test_client()

def test_compact_result_assets_are_available(client):
    response = client.get("/static/js/assessment.js")
    assert response.status_code == 200
    assert "ПОВЫШЕННЫЙ РИСК".encode("utf-8") in response.data
    assert "Расчётная температура на глубине 10 см".encode("utf-8") in response.data
    assert "Рекомендации и источники".encode("utf-8") in response.data
    assert b"DEGREE_DAYS_ABOVE_10C" in response.data
    assert b"SATURATION_DEFICIT" in response.data
    assert "Для активности клещей: от 10 °C".encode("utf-8") in response.data
    assert "Благоприятный диапазон: 15–25 °C".encode("utf-8") in response.data
    assert "Справочно".encode("utf-8") in response.data

def test_compact_result_uses_russian_date_format(client):
    response = client.get("/static/js/assessment.js")
    assert response.status_code == 200
    assert b"dateRu" in response.data


def test_compact_result_contains_weather_summary(client):
    response = client.get("/static/js/assessment.js")
    assert response.status_code == 200

    assert "ПОГОДА СЕЙЧАС".encode("utf-8") in response.data
    assert "Температура".encode("utf-8") in response.data
    assert "Влажность".encode("utf-8") in response.data
    assert "Осадки".encode("utf-8") in response.data
    assert "Ветер".encode("utf-8") in response.data
    assert "Данные на".encode("utf-8") in response.data
    assert b"input_snapshot" in response.data
    assert b"current_weather" in response.data


def test_weather_summary_is_hidden_without_current_weather(client):
    response = client.get("/static/js/assessment.js")
    assert response.status_code == 200

    assert b'if(!w)return""' in response.data
