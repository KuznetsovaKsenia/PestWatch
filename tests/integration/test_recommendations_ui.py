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


def test_dialog_contains_recommendations_target(client):
    response = client.get("/")

    assert response.status_code == 200
    assert (
        b'id="risk-details-recommendations"'
        in response.data
    )


def test_recommendations_support_all_four_threats(client):
    text = script(client)

    assert "function tickRecommendations" in text
    assert "function cabbageAphidRecommendations" in text
    assert "function coloradoBeetleRecommendations" in text
    assert "function codlingMothRecommendations" in text

    assert 'result.threat_code==="TICK"' in text
    assert 'result.threat_code==="CABBAGE_APHID"' in text
    assert 'result.threat_code==="COLORADO_BEETLE"' in text
    assert 'result.threat_code==="CODLING_MOTH"' in text


def test_tick_low_risk_uses_approved_plain_language(client):
    text = script(client)

    assert (
        "Текущая погода менее благоприятна для активности клещей, "
        "но это не означает, что клещей рядом нет."
        in text
    )

    assert (
        "При прогулках в лесу, парках и местах с высокой травой "
        "всё равно стоит соблюдать меры защиты."
        in text
    )


def test_cabbage_aphid_recommendations_use_approved_explanations(client):
    text = script(client)

    assert (
        "Если вы обнаружили тлю, осмотрите несколько растений "
        "и оцените, насколько широко она распространилась."
        in text
    )

    assert "божьи коровки" in text
    assert "пастушью сумку" in text
    assert "дикую редьку" not in text


def test_colorado_recommendations_use_plain_language_examples(client):
    text = script(client)

    assert "томаты и баклажаны" in text
    assert "чёрный паслён" in text

    assert (
        "не выращивайте картофель несколько лет подряд "
        "на одном и том же месте"
        in text
    )

    assert "чередуйте его с другими культурами" in text


def test_codling_moth_recommendations_preserve_activity_semantics(client):
    text = script(client)

    assert "периода возможной сезонной активности" in text
    assert (
        "Температурная оценка PestWatch не подтверждает "
        "фактический лёт плодожорки."
        in text
    )
    assert "феромонные ловушки" in text


def test_recommendations_do_not_auto_prescribe_chemical_treatment(client):
    text = script(client)
    slice_34b = text.split(
        "SLICE 3.4B — RECOMMENDATIONS UI",
        1,
    )[1]

    prohibited = [
        "примените инсектицид",
        "используйте инсектицид",
        "обработайте инсектицидом",
        "проведите химическую обработку",
        "обязательно обработайте",
    ]

    for phrase in prohibited:
        assert phrase not in slice_34b.lower()


def test_recommendations_slice_does_not_fetch_or_recalculate(client):
    text = script(client)
    slice_34b = text.split(
        "SLICE 3.4B — RECOMMENDATIONS UI",
        1,
    )[1]

    assert "fetch(" not in slice_34b
    assert "/api/" not in slice_34b
    assert "Math." not in slice_34b


def test_recommendations_are_bound_when_modal_opens(client):
    text = script(client)

    assert "function bindRecommendations(result)" in text
    assert "bindRecommendations(result);" in text
    assert (
        "riskDetailsRecommendations.innerHTML="
        "recommendationsHtml(result)"
        in text
    )


def test_recommendation_styles_exist(client):
    text = client.get(
        "/static/css/styles.css"
    ).data.decode("utf-8")

    assert ".recommendation-details" in text
    assert ".recommendation-item" in text
    assert ".recommendation-item--attention" in text
    assert ".recommendation-item--note" in text
