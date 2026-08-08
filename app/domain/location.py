from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    name: str
    region: str | None
    country: str
    latitude: float
    longitude: float

    def __post_init__(self):
        if not -90 <= self.latitude <= 90:
            raise ValueError(
                "Latitude must be between -90 and 90 degrees."
            )

        if not -180 <= self.longitude <= 180:
            raise ValueError(
                "Longitude must be between -180 and 180 degrees."
            )