class GeocodingIntegrationError(Exception):
    """Base exception for geocoding integration errors."""


class GeocodingTimeoutError(GeocodingIntegrationError):
    """Geocoding provider did not respond within the configured timeout."""


class GeocodingConnectionError(GeocodingIntegrationError):
    """Connection to the geocoding provider failed."""


class GeocodingResponseError(GeocodingIntegrationError):
    """Geocoding provider returned an invalid HTTP or JSON response."""


class GeocodingDataError(GeocodingIntegrationError):
    """Geocoding response contains invalid data for mapping."""
