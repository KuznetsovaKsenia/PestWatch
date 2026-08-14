import threading

import pytest
from werkzeug.serving import make_server

from app import create_app, db
from app.config.settings import TestConfig
from app.seed.threat_catalog import (
    seed_threat_catalog,
)
from tests.e2e.support import (
    build_deterministic_assessment_services,
)

def pytest_collection_modifyitems(items):
    for item in items:
        if "tests/e2e" in item.nodeid.replace("\\", "/"):
            item.add_marker(pytest.mark.e2e)
            

class E2ETestConfig(TestConfig):
    pass


@pytest.fixture(scope="session")
def e2e_app(tmp_path_factory):
    database_dir = (
        tmp_path_factory.mktemp(
            "pestwatch-e2e"
        )
    )

    database_path = (
        database_dir
        / "pestwatch-e2e.db"
    )

    E2ETestConfig.SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///"
        f"{database_path.as_posix()}"
    )

    app = create_app(
        E2ETestConfig,
        assessment_services_builder=(
            build_deterministic_assessment_services
        ),
    )

    with app.app_context():
        db.create_all()
        seed_threat_catalog()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(autouse=True)
def clean_e2e_database(e2e_app):
    with e2e_app.app_context():
        db.session.remove()

        for table in reversed(
            db.metadata.sorted_tables
        ):
            db.session.execute(
                table.delete()
            )

        db.session.commit()

        seed_threat_catalog()

    yield

@pytest.fixture(scope="session")
def live_server(e2e_app):
    server = make_server(
        "127.0.0.1",
        0,
        e2e_app,
        threaded=True,
    )

    port = server.server_port

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()

    yield (
        f"http://127.0.0.1:{port}"
    )

    server.shutdown()
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def base_url(live_server):
    return live_server