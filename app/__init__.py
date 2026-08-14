import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from app.config.settings import Config


db = SQLAlchemy()


def create_app(
    config_class=Config,
    assessment_services_builder=None,
):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from app import models  # noqa: F401
    from app.bootstrap import build_assessment_services
    from app.controllers import (
        create_assessment_api,
        create_assessment_history_web,
        threat_api,
        threat_web,
    )
    from app.seed.threat_catalog import (
        seed_threat_catalog,
    )

    services_builder = (
        assessment_services_builder
        or build_assessment_services
    )

    (
        assessment_execution_service,
        assessment_history_service,
        location_service,
    ) = services_builder(app.config)

    app.register_blueprint(threat_api)
    app.register_blueprint(threat_web)

    app.register_blueprint(
        create_assessment_history_web(
            history_service=(
                assessment_history_service
            )
        )
    )

    app.register_blueprint(
        create_assessment_api(
            execution_service=(
                assessment_execution_service
            ),
            history_service=(
                assessment_history_service
            ),
            location_service=location_service,
        )
    )

    @app.get("/")
    def index():
        return render_template(
            "index.html"
        )

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        seed_threat_catalog()

        click.echo(
            "PestWatch database initialized."
        )

    return app