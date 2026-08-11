from datetime import date

from app.domain import (
    AssessmentInputSnapshot,
    Location,
    RiskInputCapability,
    RiskResult,
    RiskStatus,
    UserProfile,
)
from app.integrations.weather import WeatherIntegrationError
from app.risk import (
    CodlingMothSeasonStartDetector,
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
        season_start_detector: (
            CodlingMothSeasonStartDetector | None
        ) = None,
    ):
        self._threat_service = threat_service
        self._weather_service = weather_service
        self._historical_weather_service = (
            historical_weather_service
        )
        self._input_requirements = input_requirements
        self._evaluator = evaluator
        self._season_start_detector = (
            season_start_detector
            or CodlingMothSeasonStartDetector()
        )

    def evaluate(
        self,
        *,
        location: Location,
        profile: UserProfile,
        assessment_date: date,
        historical_start_date: date | None = None,
    ) -> tuple[RiskResult, ...]:
        results, _ = self._evaluate(
            location=location,
            profile=profile,
            assessment_date=assessment_date,
            historical_start_date=(
                historical_start_date
            ),
            capture_snapshot=False,
        )

        return results

    def evaluate_with_snapshot(
        self,
        *,
        location: Location,
        profile: UserProfile,
        assessment_date: date,
        historical_start_date: date | None = None,
    ) -> tuple[
        tuple[RiskResult, ...],
        AssessmentInputSnapshot,
    ]:
        results, snapshot = self._evaluate(
            location=location,
            profile=profile,
            assessment_date=assessment_date,
            historical_start_date=(
                historical_start_date
            ),
            capture_snapshot=True,
        )

        assert snapshot is not None

        return results, snapshot

    def _evaluate(
        self,
        *,
        location: Location,
        profile: UserProfile,
        assessment_date: date,
        historical_start_date: date | None,
        capture_snapshot: bool,
    ) -> tuple[
        tuple[RiskResult, ...],
        AssessmentInputSnapshot | None,
    ]:
        threats = (
            self._threat_service
            .get_threats_for_profile(
                profile
            )
        )

        requirements_by_threat = {
            threat.code: self._input_requirements.get(
                threat.code
            )
            for threat in threats
        }

        required_capabilities = (
            frozenset().union(
                *requirements_by_threat.values()
            )
        )

        weather = None
        historical_observations = None
        degree_days_temperatures = None
        degree_days_season_started = None

        soil_temperature_estimate = None
        degree_days = None
        saturation_deficit = None

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
                    self._weather_service
                    .get_current_weather(
                        location
                    )
                )
            except WeatherIntegrationError as exc:
                failed_capabilities[
                    RiskInputCapability
                    .CURRENT_WEATHER
                ] = str(exc)

        if (
            RiskInputCapability.DEGREE_DAYS_10C
            in required_capabilities
        ):
            (
                acquisition_start_date,
                automatic_period,
            ) = self._historical_acquisition_start(
                assessment_date=assessment_date,
                historical_start_date=(
                    historical_start_date
                ),
            )

            try:
                historical_observations = (
                    self._historical_weather_service
                    .get_daily_temperatures(
                        location=location,
                        start_date=acquisition_start_date,
                        end_date=assessment_date,
                    )
                )

                if automatic_period:
                    season_start = (
                        self._season_start_detector
                        .find_start(
                            historical_observations
                        )
                    )

                    degree_days_season_started = (
                        season_start is not None
                    )

                    degree_days_temperatures = (
                        self._slice_from_date(
                            historical_observations,
                            season_start,
                        )
                        if season_start is not None
                        else ()
                    )
                else:
                    degree_days_season_started = True
                    degree_days_temperatures = (
                        historical_observations
                    )

            except WeatherIntegrationError as exc:
                failed_capabilities[
                    RiskInputCapability
                    .DEGREE_DAYS_10C
                ] = str(exc)

        results = []

        for threat in threats:
            capabilities = (
                requirements_by_threat[
                    threat.code
                ]
            )

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
                        explanation=(
                            capability_error
                        ),
                    )
                )
                continue

            threat_weather = (
                weather
                if (
                    RiskInputCapability
                    .CURRENT_WEATHER
                    in capabilities
                )
                else None
            )

            threat_historical_temperatures = (
                degree_days_temperatures
                if (
                    RiskInputCapability
                    .DEGREE_DAYS_10C
                    in capabilities
                )
                else None
            )

            threat_season_started = (
                degree_days_season_started
                if (
                    RiskInputCapability
                    .DEGREE_DAYS_10C
                    in capabilities
                )
                else None
            )

            try:
                if capture_snapshot:
                    (
                        result,
                        context,
                    ) = (
                        self._evaluator
                        .evaluate_with_context(
                            threat.code,
                            weather=threat_weather,
                            historical_temperatures=(
                                threat_historical_temperatures
                            ),
                            degree_days_season_started=(
                                threat_season_started
                            ),
                        )
                    )

                    if (
                        context
                        .soil_temperature_10cm_estimate
                        is not None
                    ):
                        soil_temperature_estimate = (
                            context
                            .soil_temperature_10cm_estimate
                        )

                    if (
                        context.degree_days_10c
                        is not None
                    ):
                        degree_days = (
                            context.degree_days_10c
                        )

                    if (
                        context.saturation_deficit_mm_hg
                        is not None
                    ):
                        saturation_deficit = (
                            context.saturation_deficit_mm_hg
                        )

                else:
                    result = (
                        self._evaluator.evaluate(
                            threat.code,
                            weather=threat_weather,
                            historical_temperatures=(
                                threat_historical_temperatures
                            ),
                            degree_days_season_started=(
                                threat_season_started
                            ),
                        )
                    )

            except RiskInputUnavailableError as exc:
                result = self._error_result(
                    threat_code=threat.code,
                    explanation=str(exc),
                )

            results.append(result)

        snapshot = None

        if capture_snapshot:
            snapshot = AssessmentInputSnapshot(
                current_weather=weather,
                soil_temperature_10cm_estimate=(
                    soil_temperature_estimate
                ),
                degree_days_10c=degree_days,
                saturation_deficit_mm_hg=(
                    saturation_deficit
                ),
                historical_observations=(
                    historical_observations
                ),
            )

        return tuple(results), snapshot

    @staticmethod
    def _historical_acquisition_start(
        *,
        assessment_date: date,
        historical_start_date: date | None,
    ) -> tuple[date, bool]:
        if historical_start_date is not None:
            if historical_start_date > assessment_date:
                raise HistoricalPeriodRequiredError(
                    "Historical start date cannot be "
                    "after assessment date."
                )

            return historical_start_date, False

        return date(
            assessment_date.year,
            1,
            1,
        ), True

    @staticmethod
    def _slice_from_date(
        observations,
        start_date: date,
    ):
        return tuple(
            observation
            for observation in observations
            if observation.date >= start_date
        )

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
