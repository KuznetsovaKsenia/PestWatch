from unittest.mock import Mock, patch

from app import create_app
from app.config.settings import TestConfig
from app.domain import WeatherData
from app.integrations.weather import (
    WeatherAdapter,
    WeatherClient,
)


@patch("app.integrations.weather.client.requests.get")
def test_weather_integration_uses_config_and_maps_response(mock_get):
    app = create_app(TestConfig)

    response = Mock()
    response.json.return_value = {
        "current": {
            "time": "2026-08-08T19:00",
            "temperature_2m": 18.4,
            "relative_humidity_2m": 67.0,
            "precipitation": 0.0,
            "wind_speed_10m": 3.2,
            "soil_temperature_0cm": 16.1,
        }
    }

    mock_get.return_value = response

    with app.app_context():
        client = WeatherClient(
            base_url=app.config["WEATHER_API_BASE_URL"],
            timeout_seconds=app.config[
                "WEATHER_API_TIMEOUT_SECONDS"
            ],
        )

        adapter = WeatherAdapter()

        payload = client.get_current_weather(
            latitude=55.7558,
            longitude=37.6173,
        )

        weather = adapter.to_weather_data(payload)

    assert isinstance(weather, WeatherData)

    assert weather.temperature == 18.4
    assert weather.humidity == 67.0
    assert weather.precipitation == 0.0
    assert weather.wind_speed == 3.2
    assert weather.soil_temperature == 16.1

    mock_get.assert_called_once()

    _, kwargs = mock_get.call_args

    assert kwargs["timeout"] == app.config[
        "WEATHER_API_TIMEOUT_SECONDS"
    ]

    assert kwargs["params"]["latitude"] == 55.7558
    assert kwargs["params"]["longitude"] == 37.6173

    assert kwargs["params"]["temperature_unit"] == "celsius"
    assert kwargs["params"]["wind_speed_unit"] == "ms"
    assert kwargs["params"]["precipitation_unit"] == "mm"
    assert kwargs["params"]["timezone"] == "auto"