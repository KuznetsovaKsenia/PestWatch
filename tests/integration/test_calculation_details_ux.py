import pytest

from app import create_app
from app.config.settings import TestConfig


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


def test_factor_cards_preserve_decimal_precision(client):
    text = client.get(
        "/static/js/assessment.js"
    ).data.decode("utf-8")

    assert (
        "function factorView(f,threatCode,a)"
        "{const v=temperatureValue(f.actual_value);"
        in text
    )


def test_calculation_details_use_user_facing_terms(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    slice_33 = text.split("SLICE 3.3 — CALCULATION DETAILS", 1)[1]

    assert "Порог модели" not in slice_33
    assert "Благоприятный диапазон модели" not in slice_33
    assert "Не участвует в текущей модели" not in slice_33
    assert "Условие для оценки" in slice_33
    assert "Благоприятный диапазон" in slice_33
    assert "Не влияет на текущую оценку риска" in slice_33


def test_tick_saturation_deficit_is_explained(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    assert "Дефицит насыщения показывает" in text
    assert "насколько воздух сухой" in text
    assert "чем меньше значение" in text


def test_colorado_soil_calculation_uses_depth_wording(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    assert 'detailRow("Температура почвы на глубине 10 см"' in text
    assert 'detailRow("Глубина оценки","10 см")' not in text


def test_linear_interpolation_is_explained(client):
    text = client.get("/static/js/assessment.js").data.decode("utf-8")
    assert "Линейная интерполяция рассчитывает" in text
    assert "на глубине 6 и 18 см" in text
