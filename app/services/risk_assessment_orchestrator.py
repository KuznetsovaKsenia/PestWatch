from datetime import date

from app.domain import (
    Location,
    RiskInputCapability,
    RiskResult,
    RiskStatus,
    UserProfile,
)
from app.integrations.weather import WeatherIntegrationError
from app.risk import (
    RiskInputRequirements,
    RiskInputUnavailableError,
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
        historical_temperatures = None

        failed_capabilities: dict[
            RiskInputCapability,
            str,
        ] = {}

        if (
            RiskInputCapability.CURRENT_WEATHER
            in required_capabilities
        ):
            try:
                weather = (
                    self._weather_service.get_current_weather(
                        location
                    )
                )
            except WeatherIntegrationError as exc:
                failed_capabilities[
                    RiskInputCapability.CURRENT_WEATHER
                ] = str(exc)

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

            try:
                historical_temperatures = (
                    self._historical_weather_service
                    .get_daily_temperatures(
                        location=location,
                        start_date=historical_start_date,
                        end_date=assessment_date,
                    )
                )
            except WeatherIntegrationError as exc:
                failed_capabilities[
                    RiskInputCapability.DEGREE_DAYS_10C
                ] = str(exc)

        results = []

        for threat in threats:
            capabilities = requirements_by_threat[
                threat.code
            ]

            capability_error = (
                self._find_capability_error(
                    capabilities=capabilities,
                    failed_capabilities=(
                        failed_capabilities
                    ),
                )
            )

            if capability_error is not None:
                results.append(
                    self._error_result(
                        threat_code=threat.code,
                        explanation=capability_error,
                    )
                )
                continue

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

            try:
                result = self._evaluator.evaluate(
                    threat.code,
                    weather=threat_weather,
                    historical_temperatures=(
                        threat_historical_temperatures
                    ),
                )
            except RiskInputUnavailableError as exc:
                result = self._error_result(
                    threat_code=threat.code,
                    explanation=str(exc),
                )

            results.append(result)

        return tuple(results)

    @staticmethod
    def _find_capability_error(
        *,
        capabilities: frozenset[
            RiskInputCapability
        ],
        failed_capabilities: dict[
            RiskInputCapability,
            str,
        ],
    ) -> str | None:
        for capability in capabilities:
            if capability in failed_capabilities:
                return failed_capabilities[
                    capability
                ]

        return None

    @staticmethod
    def _error_result(
        *,
        threat_code: str,
        explanation: str,
    ) -> RiskResult:
        return RiskResult(
            threat_code=threat_code,
            status=RiskStatus.ERROR,
            risk_level=None,
            factors=(),
            explanation=explanation,
        )