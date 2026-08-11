from app.domain import (
    DailyTemperature,
    RiskContext,
    RiskInputCapability,
    WeatherData,
)
from app.risk.input_requirements import RiskInputRequirements
from app.weather import (
    DegreeDaysCalculator,
    SoilTemperatureEstimator,
)


class RiskInputUnavailableError(RuntimeError):
    pass


class RiskContextPreparer:
    def __init__(
        self,
        requirements: RiskInputRequirements,
        soil_temperature_estimator: SoilTemperatureEstimator,
        degree_days_calculator: DegreeDaysCalculator,
    ):
        self._requirements = requirements
        self._soil_temperature_estimator = (
            soil_temperature_estimator
        )
        self._degree_days_calculator = (
            degree_days_calculator
        )

    def prepare(
        self,
        threat_code: str,
        *,
        weather: WeatherData | None = None,
        historical_temperatures: (
            tuple[DailyTemperature, ...] | None
        ) = None,
    ) -> RiskContext:
        capabilities = self._requirements.get(
            threat_code
        )

        self._validate_available_inputs(
            capabilities=capabilities,
            weather=weather,
            historical_temperatures=(
                historical_temperatures
            ),
        )

        soil_temperature_estimate = None

        if (
            RiskInputCapability.SOIL_TEMPERATURE_10CM
            in capabilities
        ):
            soil_temperature_estimate = (
                self._soil_temperature_estimator
                .estimate_at_10cm(
                    temperature_6cm=(
                        weather.soil_temperature_6cm
                    ),
                    temperature_18cm=(
                        weather.soil_temperature_18cm
                    ),
                )
            )

        degree_days = None

        if (
            RiskInputCapability.DEGREE_DAYS_10C
            in capabilities
        ):
            degree_days = (
                self._degree_days_calculator.calculate(
                    historical_temperatures
                )
            )

        return RiskContext(
            weather=weather,
            soil_temperature_10cm_estimate=(
                soil_temperature_estimate
            ),
            degree_days_10c=degree_days,
        )

    @staticmethod
    def _validate_available_inputs(
        *,
        capabilities: frozenset[RiskInputCapability],
        weather: WeatherData | None,
        historical_temperatures: (
            tuple[DailyTemperature, ...] | None
        ),
    ) -> None:
        if (
            RiskInputCapability.CURRENT_WEATHER
            in capabilities
            and weather is None
        ):
            raise RiskInputUnavailableError(
                "Current weather input is unavailable."
            )

        if (
            RiskInputCapability.SOIL_TEMPERATURE_10CM
            in capabilities
            and weather is None
        ):
            raise RiskInputUnavailableError(
                "Current weather input is required "
                "for soil temperature estimation."
            )

        if (
            RiskInputCapability.DEGREE_DAYS_10C
            in capabilities
            and historical_temperatures is None
        ):
            raise RiskInputUnavailableError(
                "Historical temperature input is unavailable."
            )