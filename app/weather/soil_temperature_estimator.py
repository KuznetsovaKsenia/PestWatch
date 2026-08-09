from app.domain import (
    SoilTemperatureEstimate,
    SoilTemperatureEstimateMethod,
)


class SoilTemperatureEstimator:
    SOURCE_DEPTH_1_CM = 6.0
    TARGET_DEPTH_CM = 10.0
    SOURCE_DEPTH_2_CM = 18.0

    def estimate_at_10cm(
        self,
        temperature_6cm: float | None,
        temperature_18cm: float | None,
    ) -> SoilTemperatureEstimate | None:
        if (
            temperature_6cm is None
            or temperature_18cm is None
        ):
            return None

        temperature = self._interpolate(
            depth_1=self.SOURCE_DEPTH_1_CM,
            temperature_1=temperature_6cm,
            depth_2=self.SOURCE_DEPTH_2_CM,
            temperature_2=temperature_18cm,
            target_depth=self.TARGET_DEPTH_CM,
        )

        return SoilTemperatureEstimate(
            depth_cm=self.TARGET_DEPTH_CM,
            temperature=temperature,
            source_depths_cm=(
                self.SOURCE_DEPTH_1_CM,
                self.SOURCE_DEPTH_2_CM,
            ),
            source_temperatures=(
                temperature_6cm,
                temperature_18cm,
            ),
            method=(
                SoilTemperatureEstimateMethod.LINEAR_INTERPOLATION
            ),
        )

    @staticmethod
    def _interpolate(
        *,
        depth_1: float,
        temperature_1: float,
        depth_2: float,
        temperature_2: float,
        target_depth: float,
    ) -> float:
        return temperature_1 + (
            temperature_2 - temperature_1
        ) * (
            target_depth - depth_1
        ) / (
            depth_2 - depth_1
        )