from datetime import date, timedelta

import pytest

from app import create_app, db
from app.config.settings import TestConfig
from app.integrations.geocoding import (
    OpenMeteoGeocodingClient,
)
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


@pytest.fixture(autouse=True)
def deterministic_geocoding(monkeypatch):
    calls = []

    def fake_search_locations(
        self,
        name,
    ):
        calls.append(name)

        return {
            "results": [
                {
                    "name": "Москва",
                    "admin1": "Москва",
                    "country": "Россия",
                    "latitude": 55.7558,
                    "longitude": 37.6173,
                }
            ]
        }

    monkeypatch.setattr(
        OpenMeteoGeocodingClient,
        "search_locations",
        fake_search_locations,
    )

    return calls


def assessment_request(
    *,
    profile: str,
) -> dict:
    return {
        "location": {
            "name": "Москва",
            "region": "Москва",
            "country": "Россия",
        },
        "profile": profile,
    }


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
    season_start_date: date,
) -> dict:
    days = (
        end_date - start_date
    ).days + 1

    dates = [
        start_date + timedelta(days=index)
        for index in range(days)
    ]

    return {
        "daily": {
            "time": [
                observation_date.isoformat()
                for observation_date in dates
            ],
            "temperature_2m_mean": [
                20.0
                if observation_date >= season_start_date
                else 5.0
                for observation_date in dates
            ],
        }
    }


def test_human_assessment_persists_current_weather_and_history_does_not_recalculate(
    client,
    monkeypatch,
    deterministic_geocoding,
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

    assert deterministic_geocoding == [
        "Москва"
    ]

    assert created["profile"] == "HUMAN"

    assert created["location"] == {
        "name": "Москва",
        "region": "Москва",
        "country": "Россия",
        "latitude": pytest.approx(
            55.7558
        ),
        "longitude": pytest.approx(
            37.6173
        ),
    }

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
        ["saturation_deficit_mm_hg"]
        is not None
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

    history_body = history_response.get_json()

    assert history_body["success"] is True
    assert len(history_body["data"]) == 1

    assert (
        history_body["data"][0]["id"]
        == assessment_id
    )

    assert weather_calls == 1
    assert historical_calls == 0
    assert deterministic_geocoding == ["Москва"]

    detail_response = client.get(
        f"/api/assessments/{assessment_id}"
    )

    assert detail_response.status_code == 200

    stored = detail_response.get_json()["data"]

    assert stored == created
    assert weather_calls == 1
    assert historical_calls == 0
    assert deterministic_geocoding == ["Москва"]


def test_vegetable_garden_assessment_shares_weather_and_persists_t10_without_recalculation(
    client,
    monkeypatch,
    deterministic_geocoding,
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

        assert latitude == pytest.approx(55.7558)
        assert longitude == pytest.approx(37.6173)

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

    created = create_response.get_json()["data"]
    assessment_id = created["id"]

    assert deterministic_geocoding == ["Москва"]
    assert created["profile"] == "VEGETABLE_GARDEN"
    assert weather_calls == 1
    assert historical_calls == 0

    current_weather = (
        created["input_snapshot"]
        ["current_weather"]
    )

    assert current_weather is not None
    assert current_weather["temperature"] == pytest.approx(25.5)
    assert current_weather["humidity"] == pytest.approx(65.0)

    soil_estimate = (
        created["input_snapshot"]
        ["soil_temperature_10cm_estimate"]
    )

    assert soil_estimate is not None
    assert soil_estimate["depth_cm"] == pytest.approx(10.0)
    assert soil_estimate["source_depths_cm"] == [6.0, 18.0]
    assert soil_estimate["source_temperatures"] == [16.0, 10.0]
    assert soil_estimate["temperature"] == pytest.approx(14.0)
    assert soil_estimate["method"] == "LINEAR_INTERPOLATION"

    assert created["input_snapshot"]["degree_days_10c"] is None
    assert created["input_snapshot"]["historical_observations"] is None

    assert len(created["risk_results"]) == 2

    results_by_threat = {
        result["threat_code"]: result
        for result in created["risk_results"]
    }

    assert set(results_by_threat) == {
        "COLORADO_BEETLE",
        "CABBAGE_APHID",
    }

    colorado = results_by_threat["COLORADO_BEETLE"]
    assert colorado["status"] == "CALCULATED"
    assert colorado["factors"][0]["factor"] == "SOIL_TEMPERATURE_10CM"
    assert colorado["factors"][0]["actual_value"] == pytest.approx(14.0)

    aphid = results_by_threat["CABBAGE_APHID"]
    assert aphid["status"] == "CALCULATED"

    assert len(aphid["factors"]) == 1

    aphid_temperature = aphid["factors"][0]

    assert (
        aphid_temperature["factor"]
        == "AIR_TEMPERATURE"
    )

    assert (
        aphid_temperature["actual_value"]
        == pytest.approx(25.5)
    )

    assert (
        created["input_snapshot"]
        ["current_weather"]
        ["humidity"]
        == pytest.approx(65.0)
    )

    history_response = client.get("/api/assessments")
    assert history_response.status_code == 200
    assert weather_calls == 1
    assert historical_calls == 0
    assert deterministic_geocoding == ["Москва"]

    detail_response = client.get(
        f"/api/assessments/{assessment_id}"
    )

    assert detail_response.status_code == 200
    stored = detail_response.get_json()["data"]
    assert stored == created
    assert weather_calls == 1
    assert historical_calls == 0
    assert deterministic_geocoding == ["Москва"]


def test_garden_assessment_detects_season_start_persists_degree_days_and_history_does_not_recalculate(
    client,
    monkeypatch,
    deterministic_geocoding,
):
    weather_calls = 0
    historical_calls = 0

    assessment_date = date.today()
    detected_season_start = (
        assessment_date - timedelta(days=12)
    )
    acquisition_start = date(
        assessment_date.year,
        1,
        1,
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

        assert latitude == pytest.approx(55.7558)
        assert longitude == pytest.approx(37.6173)
        assert start_date == acquisition_start
        assert end_date == assessment_date

        return historical_weather_payload(
            start_date=start_date,
            end_date=end_date,
            season_start_date=detected_season_start,
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
        ),
    )

    assert create_response.status_code == 201

    created = create_response.get_json()["data"]
    assessment_id = created["id"]

    assert deterministic_geocoding == ["Москва"]
    assert created["profile"] == "GARDEN"

    assert (
        created["historical_start_date"]
        == detected_season_start.isoformat()
    )

    assert weather_calls == 0
    assert historical_calls == 1

    assert created["input_snapshot"]["current_weather"] is None
    assert (
        created["input_snapshot"]
        ["soil_temperature_10cm_estimate"]
        is None
    )

    historical_observations = (
        created["input_snapshot"]
        ["historical_observations"]
    )

    expected_acquired_days = (
        assessment_date - acquisition_start
    ).days + 1

    assert len(historical_observations) == expected_acquired_days

    degree_days = created["input_snapshot"]["degree_days_10c"]

    assert degree_days is not None
    assert degree_days["base_temperature"] == pytest.approx(10.0)
    assert degree_days["total"] == pytest.approx(130.0)
    assert degree_days["period_start"] == detected_season_start.isoformat()
    assert degree_days["period_end"] == assessment_date.isoformat()
    assert len(degree_days["observations"]) == 13
    assert degree_days["method"] == "DAILY_MEAN_ABOVE_BASE"

    assert len(created["risk_results"]) == 1

    codling_moth = created["risk_results"][0]

    assert codling_moth["threat_code"] == "CODLING_MOTH"
    assert codling_moth["status"] == "CALCULATED"
    assert codling_moth["factors"][0]["factor"] == "DEGREE_DAYS_ABOVE_10C"
    assert codling_moth["factors"][0]["actual_value"] == pytest.approx(130.0)

    history_response = client.get("/api/assessments")
    assert history_response.status_code == 200
    assert weather_calls == 0
    assert historical_calls == 1
    assert deterministic_geocoding == ["Москва"]

    detail_response = client.get(
        f"/api/assessments/{assessment_id}"
    )

    assert detail_response.status_code == 200
    stored = detail_response.get_json()["data"]
    assert stored == created
    assert weather_calls == 0
    assert historical_calls == 1
    assert deterministic_geocoding == ["Москва"]
