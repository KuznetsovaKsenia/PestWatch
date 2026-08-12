import re

from flask import (
    Blueprint,
    abort,
    render_template,
)

from app.services import AssessmentHistoryService


_FACTOR_UNITS = {
    "AIR_TEMPERATURE": "°C",
    "SATURATION_DEFICIT": "мм рт. ст.",
    "RELATIVE_HUMIDITY": "%",
    "SOIL_TEMPERATURE_10CM": "°C",
    "DEGREE_DAYS_ABOVE_10C": "градусо-дней",
}


def _format_number(
    value,
    *,
    decimals: int = 1,
) -> str:
    if value is None:
        return "Нет данных"

    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    if number.is_integer():
        return str(int(number))

    return (
        f"{number:.{decimals}f}"
        .replace(".", ",")
    )


def _format_measurement(
    value,
    unit: str,
    *,
    decimals: int = 1,
) -> str:
    if value is None:
        return "Нет данных"

    return (
        f"{_format_number(value, decimals=decimals)} "
        f"{unit}"
    )


def _format_factor_value(
    factor,
) -> str:
    if factor.actual_value is None:
        return "Нет данных"

    unit = _FACTOR_UNITS.get(
        factor.factor
    )

    if unit is None:
        return _format_number(
            factor.actual_value
        )

    return _format_measurement(
        factor.actual_value,
        unit,
    )


_EXPECTED_PATTERN = re.compile(
    r"^\s*(>=|<=|>|<)\s*(.+?)\s*$"
)


def _format_expected(
    value: str | None,
) -> str:
    if not value:
        return ""

    match = _EXPECTED_PATTERN.match(value)

    if match is None:
        return value

    operator, operand = match.groups()

    labels = {
        ">=": "от",
        "<=": "до",
        ">": "более",
        "<": "менее",
    }

    return (
        f"{labels[operator]} {operand}"
    )


def create_assessment_history_web(
    *,
    history_service: AssessmentHistoryService,
) -> Blueprint:
    history_web = Blueprint(
        "assessment_history_web",
        __name__,
    )

    @history_web.get("/history")
    def get_assessment_history():
        assessments = (
            history_service.get_history()
        )

        return render_template(
            "history.html",
            assessments=assessments,
        )

    @history_web.get(
        "/history/<int:assessment_id>"
    )
    def get_assessment_history_detail(
        assessment_id: int,
    ):
        assessment = (
            history_service.get_assessment(
                assessment_id
            )
        )

        if assessment is None:
            abort(404)

        return render_template(
            "history_detail.html",
            assessment=assessment,
            format_number=_format_number,
            format_measurement=(
                _format_measurement
            ),
            format_factor_value=(
                _format_factor_value
            ),
            format_expected=(
                _format_expected
            ),
        )

    return history_web