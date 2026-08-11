from app import db


class AssessmentModel(db.Model):
    __tablename__ = "assessments"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        index=True,
    )

    assessment_date = db.Column(
        db.Date,
        nullable=False,
    )

    profile = db.Column(
        db.String(50),
        nullable=False,
        index=True,
    )

    location_name = db.Column(
        db.String(255),
        nullable=False,
    )

    location_region = db.Column(
        db.String(255),
        nullable=False,
    )

    location_country = db.Column(
        db.String(255),
        nullable=False,
    )

    location_latitude = db.Column(
        db.Float,
        nullable=False,
    )

    location_longitude = db.Column(
        db.Float,
        nullable=False,
    )

    historical_start_date = db.Column(
        db.Date,
        nullable=True,
    )

    risk_results = db.relationship(
    "RiskResultModel",
    back_populates="assessment",
    cascade="all, delete-orphan",
    order_by="RiskResultModel.id",
    )