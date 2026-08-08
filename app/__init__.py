from flask import Flask, app, render_template
from flask_sqlalchemy import SQLAlchemy

from app.config.settings import Config


db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    from app import models  # noqa: F401
    from app.controllers import threat_api, threat_web

    app.register_blueprint(threat_api)
    app.register_blueprint(threat_web)

    @app.get("/")
    def index():
        return render_template("index.html")

    return app