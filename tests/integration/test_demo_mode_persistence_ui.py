import pytest

from app import create_app
from app.config.settings import TestConfig


@pytest.fixture
def client():
    return create_app(
        TestConfig
    ).test_client()


def test_demo_mode_uses_session_storage(
    client,
):
    response = client.get(
        "/static/js/assessment.js"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert (
        'const DEMO_MODE_STORAGE_KEY='
        '"pestwatch.demoMode";'
        in text
    )

    assert (
        "window.sessionStorage.setItem"
        in text
    )

    assert (
        "window.sessionStorage.getItem"
        in text
    )

    assert (
        "window.sessionStorage.removeItem"
        in text
    )


def test_demo_mode_url_activates_session(
    client,
):
    response = client.get(
        "/static/js/assessment.js"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert (
        'get("demo")==="1"'
        in text
    )

    assert (
        "activateDemoModeFromUrl();"
        in text
    )


def test_base_navigation_preserves_demo_mode(
    client,
):
    response = client.get("/")

    text = response.data.decode(
        "utf-8"
    )

    assert (
        "window.sessionStorage.getItem"
        in text
    )

    assert (
        '"/?demo=1"'
        in text
    )


def test_demo_exit_clears_session_state(
    client,
):
    response = client.get(
        "/static/js/assessment.js"
    )

    text = response.data.decode(
        "utf-8"
    )

    assert (
        "disableDemoMode();"
        in text
    )