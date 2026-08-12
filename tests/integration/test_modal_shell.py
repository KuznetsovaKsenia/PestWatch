import pytest

from app import create_app
from app.config.settings import TestConfig


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


def test_home_page_contains_risk_details_dialog(
    client,
):
    response = client.get("/")

    assert response.status_code == 200
    assert (
        b'id="risk-details-dialog"'
        in response.data
    )
    assert (
        b'class="details-modal"'
        in response.data
    )
    assert (
        b'method="dialog"'
        in response.data
    )
    assert (
        b'id="risk-details-title"'
        in response.data
    )


def test_risk_details_dialog_contains_contract_sections(
    client,
):
    response = client.get("/")

    text = response.data.decode("utf-8")

    assert "Что означает результат" in text
    assert "Что рекомендуется сделать" in text
    assert "Как рассчитано" in text
    assert "Какие данные использованы" in text
    assert "Источники" in text


def test_assessment_script_contains_modal_shell_behavior(
    client,
):
    response = client.get(
        "/static/js/assessment.js"
    )

    assert response.status_code == 200

    text = response.data.decode("utf-8")

    assert "openRiskDetailsModal" in text
    assert "closeRiskDetailsModal" in text
    assert ".showModal()" in text
    assert '"close"' in text
    assert (
        "riskDetailsReturnFocus.focus()"
        in text
    )


def test_styles_contain_modal_shell(
    client,
):
    response = client.get(
        "/static/css/styles.css"
    )

    assert response.status_code == 200

    text = (
        response.data
        .decode("utf-8")
        .replace(" ", "")
    )

    assert ".details-modal" in text
    assert ".details-modal::backdrop" in text
    assert ".details-modal__content" in text
    assert "overflow-y:auto" in text