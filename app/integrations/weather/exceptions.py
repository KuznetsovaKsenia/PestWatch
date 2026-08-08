class WeatherIntegrationError(Exception):
    """Base exception for weather integration errors."""


class WeatherTimeoutError(WeatherIntegrationError):
    """Weather provider did not respond within the configured timeout."""


class WeatherConnectionError(WeatherIntegrationError):
    """Connection to the weather provider failed."""


class WeatherResponseError(WeatherIntegrationError):
    """Weather provider returned an invalid HTTP or JSON response."""


class WeatherDataError(WeatherIntegrationError):
    """Weather response does not contain valid data for mapping."""