import pytest

from app import create_app
from app.config.settings import TestConfig


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


def test_ui_uses_updated_colorado_threshold(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    assert "от 11 °C" in text
    assert "от 13 °C" not in text


def test_ui_does_not_present_130_degree_days_as_flight_start(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    assert "Для начала сезонного лёта" not in text
    assert "начала сезонного лёта" not in text
    assert "начала лёта вредителя" not in text
    assert "Условие для температурной оценки сезонной активности" in text
    assert "возможной сезонной активности" in text
