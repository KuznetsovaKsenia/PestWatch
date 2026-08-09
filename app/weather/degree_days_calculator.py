from datetime import timedelta

from app.domain import (
    DailyTemperature,
    DegreeDaysCalculationMethod,
    DegreeDaysResult,
)


class DegreeDaysCalculator:
    BASE_TEMPERATURE = 10.0

    def calculate(
        self,
        observations: tuple[DailyTemperature, ...],
    ) -> DegreeDaysResult | None:
        if not observations:
            return None

        self._validate_order(observations)

        if self._has_missing_temperature(observations):
            return None

        if self._has_calendar_gap(observations):
            return None

        total = sum(
            max(
                0.0,
                observation.mean_temperature
                - self.BASE_TEMPERATURE,
            )
            for observation in observations
        )

        return DegreeDaysResult(
            base_temperature=self.BASE_TEMPERATURE,
            total=total,
            period_start=observations[0].date,
            period_end=observations[-1].date,
            observations=observations,
            method=(
                DegreeDaysCalculationMethod.DAILY_MEAN_ABOVE_BASE
            ),
        )

    @staticmethod
    def _validate_order(
        observations: tuple[DailyTemperature, ...],
    ) -> None:
        for previous, current in zip(
            observations,
            observations[1:],
        ):
            if current.date <= previous.date:
                raise ValueError(
                    "Daily temperatures must be ordered "
                    "chronologically without duplicate dates."
                )

    @staticmethod
    def _has_missing_temperature(
        observations: tuple[DailyTemperature, ...],
    ) -> bool:
        return any(
            observation.mean_temperature is None
            for observation in observations
        )

    @staticmethod
    def _has_calendar_gap(
        observations: tuple[DailyTemperature, ...],
    ) -> bool:
        return any(
            current.date != previous.date + timedelta(days=1)
            for previous, current in zip(
                observations,
                observations[1:],
            )
        )