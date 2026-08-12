from app.domain import RiskInputCapability


class RiskInputRequirements:
    _REQUIREMENTS = {
        "TICK": frozenset({
            RiskInputCapability.CURRENT_WEATHER,
            RiskInputCapability.SATURATION_DEFICIT,
        }),
        "CABBAGE_APHID": frozenset({
            RiskInputCapability.CURRENT_WEATHER,
        }),
        "COLORADO_BEETLE": frozenset({
            RiskInputCapability.CURRENT_WEATHER,
            RiskInputCapability.SOIL_TEMPERATURE_10CM,
        }),
        "CODLING_MOTH": frozenset({
            RiskInputCapability.DEGREE_DAYS_10C,
        }),
    }

    def get(
        self,
        threat_code: str,
    ) -> frozenset[RiskInputCapability]:
        try:
            return self._REQUIREMENTS[threat_code]
        except KeyError as exc:
            raise RiskInputRequirementsNotFoundError(
                f"No risk input requirements registered for threat: {threat_code}"
            ) from exc


class RiskInputRequirementsNotFoundError(LookupError):
    pass
