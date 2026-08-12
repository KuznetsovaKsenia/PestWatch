from datetime import date, datetime, timedelta

from app.demo.scenario import DemoScenario
from app.domain import DailyTemperature, Location, WeatherData


class DemoScenarioNotFoundError(LookupError):
    """Requested demo scenario is not registered."""


class DemoScenarioRegistry:
    ASSESSMENT_DATE = date(2026, 5, 13)
    OBSERVED_AT = datetime(2026, 5, 13, 12, 0)

    def __init__(self):
        self._scenarios = self._build_scenarios()

    def get(self, scenario_id: str) -> DemoScenario:
        normalized_id = scenario_id.strip()

        for scenario in self._scenarios:
            if scenario.scenario_id == normalized_id:
                return scenario

        raise DemoScenarioNotFoundError(
            f"Unknown demo scenario: {normalized_id}"
        )

    def get_all(self) -> tuple[DemoScenario, ...]:
        return self._scenarios

    def find_by_location(
        self,
        location: Location,
    ) -> DemoScenario:
        for scenario in self._scenarios:
            if self._same_location(
                scenario.location,
                location,
            ):
                return scenario

        raise DemoScenarioNotFoundError(
            "Location does not belong to a demo scenario."
        )

    @staticmethod
    def _same_location(
        expected: Location,
        actual: Location,
    ) -> bool:
        return (
            expected.name == actual.name
            and expected.region == actual.region
            and expected.country == actual.country
            and expected.latitude == actual.latitude
            and expected.longitude == actual.longitude
        )

    @classmethod
    def _build_scenarios(
        cls,
    ) -> tuple[DemoScenario, ...]:
        return (
            cls._scenario(
                scenario_id="DEMO_A",
                name="Архангельск",
                region="Архангельская область",
                latitude=64.5401,
                longitude=40.5433,
                temperature=9.9,
                humidity=40.0,
                soil_temperature_6cm=11.9,
                soil_temperature_18cm=8.9,
                historical_temperatures=(
                    cls._history(
                        may_temperatures=(10.0,) * 13
                    )
                ),
            ),
            cls._scenario(
                scenario_id="DEMO_B",
                name="Казань",
                region="Республика Татарстан",
                latitude=55.7961,
                longitude=49.1064,
                temperature=9.9,
                humidity=60.0,
                soil_temperature_6cm=12.0,
                soil_temperature_18cm=9.0,
                historical_temperatures=(
                    cls._history(
                        may_temperatures=(
                            (20.0,) * 12
                            + (19.9,)
                        )
                    )
                ),
            ),
            cls._scenario(
                scenario_id="DEMO_C",
                name="Омск",
                region="Омская область",
                latitude=54.9885,
                longitude=73.3242,
                temperature=14.9,
                humidity=50.0,
                soil_temperature_6cm=12.1,
                soil_temperature_18cm=9.1,
                historical_temperatures=(
                    cls._history(
                        may_temperatures=(20.0,) * 13
                    )
                ),
            ),
            cls._scenario(
                scenario_id="DEMO_D",
                name="Пермь",
                region="Пермский край",
                latitude=58.0105,
                longitude=56.2502,
                temperature=15.0,
                humidity=70.0,
                soil_temperature_6cm=12.0,
                soil_temperature_18cm=9.0,
                historical_temperatures=(
                    cls._history(
                        may_temperatures=(
                            (20.0,) * 12
                            + (20.1,)
                        )
                    )
                ),
            ),
            cls._scenario(
                scenario_id="DEMO_E",
                name="Тула",
                region="Тульская область",
                latitude=54.1930,
                longitude=37.6178,
                temperature=25.0,
                humidity=80.0,
                soil_temperature_6cm=12.0,
                soil_temperature_18cm=9.0,
                historical_temperatures=(
                    cls._history(
                        may_temperatures=(22.0,) * 13
                    )
                ),
            ),
            cls._scenario(
                scenario_id="DEMO_F",
                name="Курск",
                region="Курская область",
                latitude=51.7304,
                longitude=36.1926,
                temperature=25.1,
                humidity=75.0,
                soil_temperature_6cm=11.8,
                soil_temperature_18cm=8.8,
                historical_temperatures=(
                    cls._history(
                        may_temperatures=(
                            (20.0,) * 10
                            + (10.0,) * 3
                        )
                    )
                ),
            ),
            cls._scenario(
                scenario_id="DEMO_G",
                name="Томск",
                region="Томская область",
                latitude=56.4846,
                longitude=84.9476,
                temperature=None,
                humidity=None,
                soil_temperature_6cm=None,
                soil_temperature_18cm=None,
                historical_temperatures=(
                    cls._history(
                        may_temperatures=(
                            20.0,
                            20.0,
                            20.0,
                            None,
                            20.0,
                            20.0,
                            20.0,
                            20.0,
                            20.0,
                            20.0,
                            20.0,
                            20.0,
                            20.0,
                        )
                    )
                ),
            ),
        )

    @classmethod
    def _scenario(
        cls,
        *,
        scenario_id: str,
        name: str,
        region: str,
        latitude: float,
        longitude: float,
        temperature: float | None,
        humidity: float | None,
        soil_temperature_6cm: float | None,
        soil_temperature_18cm: float | None,
        historical_temperatures: tuple[
            DailyTemperature,
            ...,
        ],
    ) -> DemoScenario:
        return DemoScenario(
            scenario_id=scenario_id,
            location=Location(
                name=name,
                region=region,
                country="Россия",
                latitude=latitude,
                longitude=longitude,
            ),
            assessment_date=cls.ASSESSMENT_DATE,
            current_weather=WeatherData(
                observed_at=cls.OBSERVED_AT,
                temperature=temperature,
                humidity=humidity,
                precipitation=0.0,
                wind_speed=2.0,
                soil_temperature=None,
                soil_temperature_6cm=(
                    soil_temperature_6cm
                ),
                soil_temperature_18cm=(
                    soil_temperature_18cm
                ),
            ),
            historical_temperatures=(
                historical_temperatures
            ),
        )

    @classmethod
    def _history(
        cls,
        *,
        may_temperatures: tuple[
            float | None,
            ...,
        ],
    ) -> tuple[DailyTemperature, ...]:
        if len(may_temperatures) != 13:
            raise ValueError(
                "Demo history must contain "
                "13 temperatures for May 1-13."
            )

        observations: list[DailyTemperature] = []

        current_date = date(2026, 1, 1)
        pre_season_end = date(2026, 4, 30)

        while current_date <= pre_season_end:
            observations.append(
                DailyTemperature(
                    date=current_date,
                    mean_temperature=10.0,
                )
            )
            current_date += timedelta(days=1)

        for index, mean_temperature in enumerate(
            may_temperatures
        ):
            observations.append(
                DailyTemperature(
                    date=date(2026, 5, 1)
                    + timedelta(days=index),
                    mean_temperature=mean_temperature,
                )
            )

        return tuple(observations)
