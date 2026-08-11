from app import db


class RiskFactorResultModel(db.Model):
    __tablename__ = "risk_factor_results"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    risk_result_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "risk_results.id"
        ),
        nullable=False,
        index=True,
    )

    factor = db.Column(
        db.String(100),
        nullable=False,
    )

    state = db.Column(
        db.String(50),
        nullable=False,
    )

    actual_value = db.Column(
        db.JSON,
        nullable=True,
    )

    expected = db.Column(
        db.Text,
        nullable=True,
    )

    explanation = db.Column(
        db.Text,
        nullable=False,
    )

    required = db.Column(
        db.Boolean,
        nullable=False,
    )

    risk_result = db.relationship(
        "RiskResultModel",
        back_populates="factors",
    )