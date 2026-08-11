from datetime import date, timedelta

import pytest

from app import create_app, db
from app.config.settings import TestConfig
from app.integrations.weather import (
    HistoricalWeatherClient,
    WeatherClient,
)
from app.seed.threat_catalog import seed_threat_catalog


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        seed_threat_catalog()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def assessment_request(
    *,
    profile: str,
    historical_start_date: date | None = None,
) -> dict:
    payload = {
        "location": {
            "name": "Москва",
            "region": "Москва",
            "country": "Россия",
            "latitude": 55.7558,
            "longitude": 37.6173,
        },
        "profile": profile,
    }

    if historical_start_date is not None:
        payload["historical_start_date"] = (
            historical_start_date.isoformat()
        )

    return payload


def current_weather_payload() -> dict:
    return {
        "current": {
            "time": "2026-08-11T12:00",
            "temperature_2m": 25.5,
            "relative_humidity_2m": 65.0,
            "precipitation": 0.0,
            "wind_speed_10m": 2.0,
            "soil_temperature_0cm": 18.0,
            "soil_temperature_6cm": 16.0,
            "soil_temperature_18cm": 10.0,
        }
    }


def historical_weather_payload(
    *,
    start_date: date,
    end_date: date,
    mean_temperature: float,
) -> dict:
    days = (
        end_date - start_date
    ).days + 1

    return {
        "daily": {
            "time": [
                (
                    start_date
                    + timedelta(days=index)
                ).isoformat()
                for index in range(days)
            ],
            "temperature_2m_mean": [
                mean_temperature
                for _ in range(days)
            ],
        }
    }


def test_human_assessment_persists_current_weather_and_history_does_not_recalculate(
    client,
    monkeypatch,
):
    weather_calls = 0
    historical_calls = 0

    def fake_get_current_weather(
        self,
        latitude,
        longitude,
    ):
        nonlocal weather_calls
        weather_calls += 1

        assert latitude == pytest.approx(
            55.7558
        )
        assert longitude == pytest.approx(
            37.6173
        )

        return current_weather_payload()

    def fail_if_historical_weather_requested(
        self,
        latitude,
        longitude,
        start_date,
        end_date,
    ):
        nonlocal historical_calls
        historical_calls += 1

        pytest.fail(
            "Historical weather must not be requested "
            "for HUMAN assessment."
        )

    monkeypatch.setattr(
        WeatherClient,
        "get_current_weather",
        fake_get_current_weather,
    )

    monkeypatch.setattr(
        HistoricalWeatherClient,
        "get_daily_mean_temperatures",
        fail_if_historical_weather_requested,
    )

    create_response = client.post(
        "/api/assessments",
        json=assessment_request(
            profile="HUMAN",
        ),
    )

    assert create_response.status_code == 201

    create_body = create_response.get_json()

    assert create_body["success"] is True

    created = create_body["data"]
    assessment_id = created["id"]

    assert created["profile"] == "HUMAN"

    assert (
        created["input_snapshot"]
        ["current_weather"]
        ["temperature"]
        == pytest.approx(25.5)
    )

    assert (
        created["input_snapshot"]
        ["current_weather"]
        ["humidity"]
        == pytest.approx(65.0)
    )

    assert (
        created["input_snapshot"]
        ["soil_temperature_10cm_estimate"]
        is None
    )

    assert (
        created["input_snapshot"]
        ["degree_days_10c"]
        is None
    )

    assert (
        created["input_snapshot"]
        ["historical_observations"]
        is None
    )

    assert len(created["risk_results"]) == 1

    assert (
        created["risk_results"][0]
        ["threat_code"]
        == "TICK"
    )

    assert (
        created["risk_results"][0]
        ["status"]
        == "CALCULATED"
    )

    assert weather_calls == 1
    assert historical_calls == 0

    history_response = client.get(
        "/api/assessments"
    )

    assert history_response.status_code == 200

    history_body = (
        history_response.get_json()
    )

    assert history_body["success"] is True
    assert len(history_body["data"]) == 1

    assert (
        history_body["data"][0]["id"]
        == assessment_id
    )

    assert weather_calls == 1
    assert historical_calls == 0

    detail_response = client.get(
        f"/api/assessments/{assessment_id}"
    )

    assert detail_response.status_code == 200

    stored = (
        detail_response
        .get_json()["data"]
    )

    assert stored == created

    assert weather_calls == 1
    assert historical_calls == 0


def test_vegetable_garden_assessment_shares_weather_and_persists_t10_without_recalculation(
    client,
    monkeypatch,
):
    weather_calls = 0
    historical_calls = 0

    def fake_get_current_weather(
        self,
        latitude,
        longitude,
    ):
        nonlocal weather_calls
        weather_calls += 1

        return current_weather_payload()

    def fail_if_historical_weather_requested(
        self,
        latitude,
        longitude,
        start_date,
        end_date,
    ):
        nonlocal historical_calls
        historical_calls += 1

        pytest.fail(
            "Historical weather must not be requested "
            "for VEGETABLE_GARDEN assessment."
        )

    monkeypatch.setattr(
        WeatherClient,
        "get_current_weather",
        fake_get_current_weather,
    )

    monkeypatch.setattr(
        HistoricalWeatherClient,
        "get_daily_mean_temperatures",
        fail_if_historical_weather_requested,
    )

    create_response = client.post(
        "/api/assessments",
        json=assessment_request(
            profile="VEGETABLE_GARDEN",
        ),
    )

    assert create_response.status_code == 201

    created = (
        create_response
        .get_json()["data"]
    )

    assessment_id = created["id"]

    assert (
        created["profile"]
        == "VEGETABLE_GARDEN"
    )

    assert weather_calls == 1
    assert historical_calls == 0

    current_weather = (
        created["input_snapshot"]
        ["current_weather"]
    )

    assert current_weather is not None

    assert (
        current_weather["temperature"]
        == pytest.approx(25.5)
    )

    assert (
        current_weather["humidity"]
        == pytest.approx(65.0)
    )

    soil_estimate = (
        created["input_snapshot"]
        ["soil_temperature_10cm_estimate"]
    )

    assert soil_estimate is not None

    assert (
        soil_estimate["depth_cm"]
        == pytest.approx(10.0)
    )

    assert (
        soil_estimate["source_depths_cm"]
        == [6.0, 18.0]
    )

    assert (
        soil_estimate["source_temperatures"]
        == [16.0, 10.0]
    )

    assert (
        soil_estimate["temperature"]
        == pytest.approx(14.0)
    )

    assert (
        soil_estimate["method"]
        == "LINEAR_INTERPOLATION"
    )

    assert (
        created["input_snapshot"]
        ["degree_days_10c"]
        is None
    )

    assert (
        created["input_snapshot"]
        ["historical_observations"]
        is None
    )

    assert len(created["risk_results"]) == 2

    results_by_threat = {
        result["threat_code"]: result
        for result in created[
            "risk_results"
        ]
    }

    assert set(results_by_threat) == {
        "COLORADO_BEETLE",
        "CABBAGE_APHID",
    }

    colorado = results_by_threat[
        "COLORADO_BEETLE"
    ]

    assert (
        colorado["status"]
        == "CALCULATED"
    )

    assert (
        colorado["factors"][0]
        ["factor"]
        == "SOIL_TEMPERATURE_10CM"
    )

    assert (
        colorado["factors"][0]
        ["actual_value"]
        == pytest.approx(14.0)
    )

    aphid = results_by_threat[
        "CABBAGE_APHID"
    ]

    assert (
        aphid["status"]
        == "CALCULATED"
    )

    aphid_factors = {
        factor["factor"]: factor
        for factor in aphid["factors"]
    }

    assert (
        aphid_factors[
            "AIR_TEMPERATURE"
        ]["actual_value"]
        == pytest.approx(25.5)
    )

    assert (
        aphid_factors[
            "RELATIVE_HUMIDITY"
        ]["actual_value"]
        == pytest.approx(65.0)
    )

    history_response = client.get(
        "/api/assessments"
    )

    assert history_response.status_code == 200

    assert weather_calls == 1
    assert historical_calls == 0

    detail_response = client.get(
        f"/api/assessments/{assessment_id}"
    )

    assert detail_response.status_code == 200

    stored = (
        detail_response
        .get_json()["data"]
    )

    assert stored == created

    assert weather_calls == 1
    assert historical_calls == 0


def test_garden_assessment_persists_degree_days_and_history_does_not_recalculate(
    client,
    monkeypatch,
):
    weather_calls = 0
    historical_calls = 0

    assessment_date = date.today()

    historical_start_date = (
        assessment_date
        - timedelta(days=12)
    )

    def fail_if_current_weather_requested(
        self,
        latitude,
        longitude,
    ):
        nonlocal weather_calls
        weather_calls += 1

        pytest.fail(
            "Current weather must not be requested "
            "for GARDEN assessment."
        )

    def fake_get_daily_mean_temperatures(
        self,
        latitude,
        longitude,
        start_date,
        end_date,
    ):
        nonlocal historical_calls
        historical_calls += 1

        assert latitude == pytest.approx(
            55.7558
        )
        assert longitude == pytest.approx(
            37.6173
        )

        assert (
            start_date
            == historical_start_date
        )

        assert (
            end_date
            == assessment_date
        )

        return historical_weather_payload(
            start_date=start_date,
            end_date=end_date,
            mean_temperature=20.0,
        )

    monkeypatch.setattr(
        WeatherClient,
        "get_current_weather",
        fail_if_current_weather_requested,
    )

    monkeypatch.setattr(
        HistoricalWeatherClient,
        "get_daily_mean_temperatures",
        fake_get_daily_mean_temperatures,
    )

    create_response = client.post(
        "/api/assessments",
        json=assessment_request(
            profile="GARDEN",
            historical_start_date=(
                historical_start_date
            ),
        ),
    )

    assert create_response.status_code == 201

    created = (
        create_response
        .get_json()["data"]
    )

    assessment_id = created["id"]

    assert created["profile"] == "GARDEN"

    assert (
        created["historical_start_date"]
        == historical_start_date.isoformat()
    )

    assert weather_calls == 0
    assert historical_calls == 1

    assert (
        created["input_snapshot"]
        ["current_weather"]
        is None
    )

    assert (
        created["input_snapshot"]
        ["soil_temperature_10cm_estimate"]
        is None
    )

    observations = (
        created["input_snapshot"]
        ["historical_observations"]
    )

    assert observations is not None
    assert len(observations) == 13

    degree_days = (
        created["input_snapshot"]
        ["degree_days_10c"]
    )

    assert degree_days is not None

    assert (
        degree_days["base_temperature"]
        == pytest.approx(10.0)
    )

    assert (
        degree_days["total"]
        == pytest.approx(130.0)
    )

    assert (
        degree_days["period_start"]
        == historical_start_date.isoformat()
    )

    assert (
        degree_days["period_end"]
        == assessment_date.isoformat()
    )

    assert (
        degree_days["method"]
        == "DAILY_MEAN_ABOVE_BASE"
    )

    assert len(created["risk_results"]) == 1

    codling_moth = (
        created["risk_results"][0]
    )

    assert (
        codling_moth["threat_code"]
        == "CODLING_MOTH"
    )

    assert (
        codling_moth["status"]
        == "CALCULATED"
    )

    assert (
        codling_moth["factors"][0]
        ["factor"]
        == "DEGREE_DAYS_ABOVE_10C"
    )

    assert (
        codling_moth["factors"][0]
        ["actual_value"]
        == pytest.approx(130.0)
    )

    history_response = client.get(
        "/api/assessments"
    )

    assert history_response.status_code == 200

    assert weather_calls == 0
    assert historical_calls == 1

    detail_response = client.get(
        f"/api/assessments/{assessment_id}"
    )

    assert detail_response.status_code == 200

    stored = (
        detail_response
        .get_json()["data"]
    )

    assert stored == created

    assert weather_calls == 0
    assert historical_calls == 1