from datetime import date

from app import db
from app.domain import (
    Assessment,
    AssessmentInputSnapshot,
    DailyTemperature,
    DegreeDaysCalculationMethod,
    DegreeDaysResult,
    Location,
    RiskFactorResult,
    RiskFactorState,
    RiskLevel,
    RiskResult,
    RiskStatus,
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
    UserProfile,
    WeatherData,
)
from app.domain.assessment_summary import AssessmentSummary
from app.models import (
    AssessmentInputSnapshotModel,
    AssessmentModel,
    RiskFactorResultModel,
    RiskResultModel,
)


class AssessmentRepository:
    def save(
        self,
        assessment: Assessment,
    ) -> Assessment:
        model = self._to_model(
            assessment
        )

        db.session.add(model)
        db.session.commit()

        return self._to_domain(model)

    def get_all(
        self,
    ) -> tuple[AssessmentSummary, ...]:
        models = db.session.execute(
            db.select(
                AssessmentModel
            ).order_by(
                AssessmentModel.created_at.desc(),
                AssessmentModel.id.desc(),
            )
        ).scalars().all()

        return tuple(
            self._to_summary(model)
            for model in models
        )

    def get_by_id(
        self,
        assessment_id: int,
    ) -> Assessment | None:
        model = db.session.get(
            AssessmentModel,
            assessment_id,
        )

        if model is None:
            return None

        return self._to_domain(model)

    def _to_model(
        self,
        assessment: Assessment,
    ) -> AssessmentModel:
        model = AssessmentModel(
            id=assessment.id,
            created_at=assessment.created_at,
            assessment_date=(
                assessment.assessment_date
            ),
            profile=assessment.profile.value,
            location_name=assessment.location.name,
            location_region=assessment.location.region,
            location_country=(
                assessment.location.country
            ),
            location_latitude=(
                assessment.location.latitude
            ),
            location_longitude=(
                assessment.location.longitude
            ),
            historical_start_date=(
                assessment.historical_start_date
            ),
        )

        model.input_snapshot = (
            self._snapshot_to_model(
                assessment.input_snapshot
            )
        )

        model.risk_results = [
            self._risk_result_to_model(
                result
            )
            for result in assessment.risk_results
        ]

        return model

    @staticmethod
    def _snapshot_to_model(
        snapshot: AssessmentInputSnapshot,
    ) -> AssessmentInputSnapshotModel:
        weather = snapshot.current_weather

        soil_estimate = (
            snapshot.soil_temperature_10cm_estimate
        )

        degree_days = snapshot.degree_days_10c

        observations = (
            snapshot.historical_observations
        )

        if (
            observations is None
            and degree_days is not None
        ):
            observations = degree_days.observations

        return AssessmentInputSnapshotModel(
            weather_observed_at=(
                weather.observed_at
                if weather is not None
                else None
            ),
            weather_temperature=(
                weather.temperature
                if weather is not None
                else None
            ),
            weather_humidity=(
                weather.humidity
                if weather is not None
                else None
            ),
            weather_precipitation=(
                weather.precipitation
                if weather is not None
                else None
            ),
            weather_wind_speed=(
                weather.wind_speed
                if weather is not None
                else None
            ),
            weather_soil_temperature=(
                weather.soil_temperature
                if weather is not None
                else None
            ),
            weather_soil_temperature_6cm=(
                weather.soil_temperature_6cm
                if weather is not None
                else None
            ),
            weather_soil_temperature_18cm=(
                weather.soil_temperature_18cm
                if weather is not None
                else None
            ),
            soil_estimate_depth_cm=(
                soil_estimate.depth_cm
                if soil_estimate is not None
                else None
            ),
            soil_estimate_temperature=(
                soil_estimate.temperature
                if soil_estimate is not None
                else None
            ),
            soil_estimate_source_depths=(
                list(
                    soil_estimate.source_depths_cm
                )
                if soil_estimate is not None
                else None
            ),
            soil_estimate_source_temperatures=(
                list(
                    soil_estimate.source_temperatures
                )
                if soil_estimate is not None
                else None
            ),
            soil_estimate_method=(
                soil_estimate.method.value
                if soil_estimate is not None
                else None
            ),
            degree_days_base_temperature=(
                degree_days.base_temperature
                if degree_days is not None
                else None
            ),
            degree_days_total=(
                degree_days.total
                if degree_days is not None
                else None
            ),
            degree_days_period_start=(
                degree_days.period_start
                if degree_days is not None
                else None
            ),
            degree_days_period_end=(
                degree_days.period_end
                if degree_days is not None
                else None
            ),
            degree_days_method=(
                degree_days.method.value
                if degree_days is not None
                else None
            ),
            historical_observations=(
                [
                    {
                        "date": observation.date.isoformat(),
                        "mean_temperature": (
                            observation.mean_temperature
                        ),
                    }
                    for observation in observations
                ]
                if observations is not None
                else None
            ),
        )

    @staticmethod
    def _risk_result_to_model(
        result: RiskResult,
    ) -> RiskResultModel:
        model = RiskResultModel(
            threat_code=result.threat_code,
            status=result.status.value,
            risk_level=(
                result.risk_level.value
                if result.risk_level is not None
                else None
            ),
            explanation=result.explanation,
        )

        model.factors = [
            RiskFactorResultModel(
                factor=factor.factor,
                state=factor.state.value,
                actual_value=factor.actual_value,
                expected=factor.expected,
                explanation=factor.explanation,
                required=factor.required,
            )
            for factor in result.factors
        ]

        return model

    @staticmethod
    def _to_summary(
        model: AssessmentModel,
    ) -> AssessmentSummary:
        return AssessmentSummary(
            id=model.id,
            created_at=model.created_at,
            assessment_date=model.assessment_date,
            profile=UserProfile(
                model.profile
            ),
            location=Location(
                name=model.location_name,
                region=model.location_region,
                country=model.location_country,
                latitude=model.location_latitude,
                longitude=model.location_longitude,
            ),
        )

    def _to_domain(
        self,
        model: AssessmentModel,
    ) -> Assessment:
        return Assessment(
            id=model.id,
            created_at=model.created_at,
            assessment_date=model.assessment_date,
            profile=UserProfile(
                model.profile
            ),
            location=Location(
                name=model.location_name,
                region=model.location_region,
                country=model.location_country,
                latitude=model.location_latitude,
                longitude=model.location_longitude,
            ),
            historical_start_date=(
                model.historical_start_date
            ),
            input_snapshot=(
                self._snapshot_to_domain(
                    model.input_snapshot
                )
            ),
            risk_results=tuple(
                self._risk_result_to_domain(
                    result
                )
                for result in model.risk_results
            ),
        )

    @staticmethod
    def _snapshot_to_domain(
        model: AssessmentInputSnapshotModel,
    ) -> AssessmentInputSnapshot:
        observations = None

        if model.historical_observations is not None:
            observations = tuple(
                DailyTemperature(
                    date=date.fromisoformat(
                        item["date"]
                    ),
                    mean_temperature=(
                        item["mean_temperature"]
                    ),
                )
                for item
                in model.historical_observations
            )

        weather = None

        if model.weather_observed_at is not None:
            weather = WeatherData(
                observed_at=model.weather_observed_at,
                temperature=model.weather_temperature,
                humidity=model.weather_humidity,
                precipitation=(
                    model.weather_precipitation
                ),
                wind_speed=model.weather_wind_speed,
                soil_temperature=(
                    model.weather_soil_temperature
                ),
                soil_temperature_6cm=(
                    model.weather_soil_temperature_6cm
                ),
                soil_temperature_18cm=(
                    model.weather_soil_temperature_18cm
                ),
            )

        soil_estimate = None

        if (
            model.soil_estimate_temperature
            is not None
        ):
            soil_estimate = SoilTemperatureEstimate(
                depth_cm=model.soil_estimate_depth_cm,
                temperature=(
                    model.soil_estimate_temperature
                ),
                source_depths_cm=tuple(
                    model.soil_estimate_source_depths
                ),
                source_temperatures=tuple(
                    model.soil_estimate_source_temperatures
                ),
                method=SoilTemperatureEstimateMethod(
                    model.soil_estimate_method
                ),
            )

        degree_days = None

        if model.degree_days_total is not None:
            degree_days = DegreeDaysResult(
                base_temperature=(
                    model.degree_days_base_temperature
                ),
                total=model.degree_days_total,
                period_start=(
                    model.degree_days_period_start
                ),
                period_end=(
                    model.degree_days_period_end
                ),
                observations=observations or (),
                method=DegreeDaysCalculationMethod(
                    model.degree_days_method
                ),
            )

        return AssessmentInputSnapshot(
            current_weather=weather,
            soil_temperature_10cm_estimate=(
                soil_estimate
            ),
            degree_days_10c=degree_days,
            historical_observations=observations,
        )

    @staticmethod
    def _risk_result_to_domain(
        model: RiskResultModel,
    ) -> RiskResult:
        return RiskResult(
            threat_code=model.threat_code,
            status=RiskStatus(
                model.status
            ),
            risk_level=(
                RiskLevel(
                    model.risk_level
                )
                if model.risk_level is not None
                else None
            ),
            factors=tuple(
                RiskFactorResult(
                    factor=factor.factor,
                    state=RiskFactorState(
                        factor.state
                    ),
                    actual_value=(
                        factor.actual_value
                    ),
                    expected=factor.expected,
                    explanation=factor.explanation,
                    required=factor.required,
                )
                for factor in model.factors
            ),
            explanation=model.explanation,
        )