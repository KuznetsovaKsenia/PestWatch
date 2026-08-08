from enum import Enum


class RiskFactorState(str, Enum):
    MATCHED = "MATCHED"
    NOT_MATCHED = "NOT_MATCHED"
    MISSING = "MISSING"