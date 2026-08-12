import pytest

from app import create_app
from app.config.settings import TestConfig


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


def test_result_action_is_real_button_with_threat_binding(
    client,
):
    response = client.get(
        "/static/js/assessment.js"
    )

    text = response.data.decode("utf-8")

    assert 'class="risk-details-trigger"' in text
    assert 'type="button"' in text
    assert "data-threat-code" in text
    assert "Рекомендации и источники →" in text


def test_assessment_is_retained_for_modal_binding(
    client,
):
    response = client.get(
        "/static/js/assessment.js"
    )

    text = response.data.decode("utf-8")

    assert "let currentAssessment=null" in text
    assert "currentAssessment=a" in text
    assert "findRiskResult" in text
    assert "currentAssessment.risk_results" in text


def test_modal_identity_is_bound_from_selected_risk_result(
    client,
):
    response = client.get(
        "/static/js/assessment.js"
    )

    text = response.data.decode("utf-8")

    assert "bindRiskDetailsIdentity" in text
    assert "riskDetailsTitle.textContent=threatName" in text
    assert "riskDetailsLevel.textContent" in text
    assert "openRiskDetailsModal(trigger)" in text


def test_dialog_contains_dynamic_identity_targets(
    client,
):
    response = client.get("/")

    assert response.status_code == 200

    assert (
        b'id="risk-details-title"'
        in response.data
    )
    assert (
        b'id="risk-details-level"'
        in response.data
    )


def test_threat_binding_does_not_fetch_or_recalculate(
    client,
):
    response = client.get(
        "/static/js/assessment.js"
    )

    text = response.data.decode("utf-8")

    binding = text.split(
        "SLICE 3.2B — THREAT BINDING",
        1,
    )[1]

    assert "fetch(" not in binding
    assert "/api/" not in binding
