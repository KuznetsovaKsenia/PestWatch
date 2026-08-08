import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///pestwatch.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WEATHER_API_BASE_URL = os.getenv(
        "WEATHER_API_BASE_URL",
        "https://api.open-meteo.com/v1/forecast",
    )

    WEATHER_API_TIMEOUT_SECONDS = float(
        os.getenv("WEATHER_API_TIMEOUT_SECONDS", "5")
    )


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"