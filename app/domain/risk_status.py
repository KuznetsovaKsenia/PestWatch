from enum import Enum


class RiskStatus(str, Enum):
    CALCULATED = "CALCULATED"
    LIMITED = "LIMITED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    ERROR = "ERROR"