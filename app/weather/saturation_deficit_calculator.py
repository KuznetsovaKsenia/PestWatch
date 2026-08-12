import math


class SaturationDeficitCalculator:
    def calculate(
        self,
        *,
        temperature: float | None,
        humidity: float | None,
    ) -> float | None:
        if temperature is None or humidity is None:
            return None

        return (
            (1.0 - humidity / 100.0)
            * 4.9463
            * math.exp(
                0.0621 * temperature
            )
        )
