from datetime import date

from app.domain import (
    Location,
    RiskInputCapability,
    RiskResult,
    UserProfile,
)
from app.risk import (
    RiskInputRequirements,
    SingleThreatRiskEvaluator,
)
from app.services.historical_weather_service import (
    HistoricalWeatherService,
)
from app.services.threat_service import ThreatService
from app.services.weather_service import WeatherService


class HistoricalPeriodRequiredError(ValueError):
    pass


class RiskAssessmentOrchestrator:
    def __init__(
        self,
        threat_service: ThreatService,
        weather_service: WeatherService,
        historical_weather_service: HistoricalWeatherService,
        input_requirements: RiskInputRequirements,
        evaluator: SingleThreatRiskEvaluator,
    ):
        self._threat_service = threat_service
        self._weather_service = weather_service
        self._historical_weather_service = (
            historical_weather_service
        )
        self._input_requirements = input_requirements
        self._evaluator = evaluator

    def evaluate(
        self,
        *,
        location: Location,
        profile: UserProfile,
        assessment_date: date,
        historical_start_date: date | None = None,
    ) -> tuple[RiskResult, ...]:
        threats = self._threat_service.get_threats_for_profile(
            profile
        )

        requirements_by_threat = {
            threat.code: self._input_requirements.get(
                threat.code
            )
            for threat in threats
        }

        required_capabilities = frozenset().union(
            *requirements_by_threat.values()
        )

        weather = None

        if (
            RiskInputCapability.CURRENT_WEATHER
            in required_capabilities
        ):
            weather = self._weather_service.get_current_weather(
                location
            )

        historical_temperatures = None

        if (
            RiskInputCapability.DEGREE_DAYS_10C
            in required_capabilities
        ):
            if historical_start_date is None:
                raise HistoricalPeriodRequiredError(
                    "Historical start date is required "
                    "for selected threats."
                )

            if historical_start_date > assessment_date:
                raise HistoricalPeriodRequiredError(
                    "Historical start date cannot be "
                    "after assessment date."
                )

            historical_temperatures = (
                self._historical_weather_service
                .get_daily_temperatures(
                    location=location,
                    start_date=historical_start_date,
                    end_date=assessment_date,
                )
            )

        results = []

        for threat in threats:
            capabilities = requirements_by_threat[
                threat.code
            ]

            threat_weather = (
                weather
                if RiskInputCapability.CURRENT_WEATHER
                in capabilities
                else None
            )

            threat_historical_temperatures = (
                historical_temperatures
                if RiskInputCapability.DEGREE_DAYS_10C
                in capabilities
                else None
            )

            result = self._evaluator.evaluate(
                threat.code,
                weather=threat_weather,
                historical_temperatures=(
                    threat_historical_temperatures
                ),
            )

            results.append(result)

        return tuple(results)