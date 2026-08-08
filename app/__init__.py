from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from app.config.settings import Config


db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    @app.get("/")
    def index():
        return render_template("index.html")

    return app