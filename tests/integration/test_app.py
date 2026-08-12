import pytest

from app import create_app, db
from app.config.settings import TestConfig


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


def test_app_can_be_created(app):
    assert app is not None


def test_home_page_returns_200(client):
    response = client.get("/")

    assert response.status_code == 200


def test_home_page_contains_project_name(client):
    response = client.get("/")

    assert b"PestWatch" in response.data


def test_home_page_contains_assessment_form(
    client,
):
    response = client.get("/")

    assert (
        b'id="assessment-form"'
        in response.data
    )


@pytest.mark.parametrize(
    ("profile", "label"),
    [
        ("HUMAN", "Человек"),
        (
            "VEGETABLE_GARDEN",
            "Огород",
        ),
        ("GARDEN", "Сад"),
    ],
)
def test_home_page_contains_supported_profiles(
    client,
    profile,
    label,
):
    response = client.get("/")

    assert (
        f'value="{profile}"'.encode()
        in response.data
    )

    assert (
        label.encode("utf-8")
        in response.data
    )


def test_home_page_contains_user_location_fields(
    client,
):
    response = client.get("/")

    required_fields = [
        "location-name",
        "location-region",
        "location-country",
    ]

    for field_id in required_fields:
        assert (
            f'id="{field_id}"'.encode()
            in response.data
        )


def test_home_page_does_not_request_coordinates(
    client,
):
    response = client.get("/")

    assert b'id="location-latitude"' not in response.data
    assert b'id="location-longitude"' not in response.data


def test_home_page_does_not_request_historical_period(
    client,
):
    response = client.get("/")

    assert (
        b'id="historical-start-date"'
        not in response.data
    )


def test_home_page_contains_enabled_assessment_submit(
    client,
):
    response = client.get("/")

    assert (
        b'id="assessment-submit"'
        in response.data
    )

    assert (
        b'type="submit"'
        in response.data
    )


def test_home_page_contains_assessment_result_container(
    client,
):
    response = client.get("/")

    assert (
        b'id="assessment-result"'
        in response.data
    )

    assert (
        b'id="risk-results"'
        in response.data
    )


def test_home_page_loads_assessment_script(
    client,
):
    response = client.get("/")

    assert (
        b"js/assessment.js"
        in response.data
    )


def test_assessment_script_is_available(
    client,
):
    response = client.get(
        "/static/js/assessment.js"
    )

    assert response.status_code == 200

    assert (
        b"/api/assessments"
        in response.data
    )


def test_database_uses_in_memory_sqlite(app):
    assert (
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ]
        == "sqlite:///:memory:"
    )


def test_database_can_be_initialized(app):
    with app.app_context():
        db.create_all()

        assert (
            db.engine.url.drivername
            == "sqlite"
        )

        assert (
            str(db.engine.url)
            == "sqlite:///:memory:"
        )

        db.drop_all()


def test_init_db_command_creates_database(app):
    runner = app.test_cli_runner()

    result = runner.invoke(
        args=["init-db"]
    )

    assert result.exit_code == 0

    assert (
        "PestWatch database initialized."
        in result.output
    )

    with app.app_context():
        inspector = db.inspect(
            db.engine
        )

        assert "threats" in (
            inspector.get_table_names()
        )

        db.drop_all()


def test_init_db_command_seeds_threat_catalog(app):
    from app.models import ThreatModel

    runner = app.test_cli_runner()

    result = runner.invoke(
        args=["init-db"]
    )

    assert result.exit_code == 0

    with app.app_context():
        threat_codes = set(
            db.session.execute(
                db.select(
                    ThreatModel.code
                )
            ).scalars()
        )

        assert threat_codes == {
            "TICK",
            "COLORADO_BEETLE",
            "CABBAGE_APHID",
            "CODLING_MOTH",
        }

        db.drop_all()
