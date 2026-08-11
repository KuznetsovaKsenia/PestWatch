from datetime import date, timedelta

from app.domain import DailyTemperature


class CodlingMothSeasonStartDetector:
    BASE_TEMPERATURE = 10.0
    CONSECUTIVE_DAYS = 3

    def find_start(
        self,
        observations: tuple[DailyTemperature, ...],
    ) -> date | None:
        self._validate_order(observations)

        streak_start: date | None = None
        streak_length = 0
        previous_date: date | None = None

        for observation in observations:
            is_consecutive = (
                previous_date is not None
                and observation.date
                == previous_date + timedelta(days=1)
            )

            is_above_base = (
                observation.mean_temperature is not None
                and observation.mean_temperature
                > self.BASE_TEMPERATURE
            )

            if not is_above_base:
                streak_start = None
                streak_length = 0
            elif streak_length == 0 or not is_consecutive:
                streak_start = observation.date
                streak_length = 1
            else:
                streak_length += 1

            if streak_length >= self.CONSECUTIVE_DAYS:
                return streak_start

            previous_date = observation.date

        return None

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
