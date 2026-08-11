from app import db


class RiskResultModel(db.Model):
    __tablename__ = "risk_results"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    assessment_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "assessments.id"
        ),
        nullable=False,
        index=True,
    )

    threat_code = db.Column(
        db.String(50),
        nullable=False,
        index=True,
    )

    status = db.Column(
        db.String(50),
        nullable=False,
    )

    risk_level = db.Column(
        db.String(50),
        nullable=True,
    )

    explanation = db.Column(
        db.Text,
        nullable=False,
    )

    assessment = db.relationship(
        "AssessmentModel",
        back_populates="risk_results",
    )

    factors = db.relationship(
        "RiskFactorResultModel",
        back_populates="risk_result",
        cascade="all, delete-orphan",
        order_by="RiskFactorResultModel.id",
    )