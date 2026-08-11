from app import db


class AssessmentInputSnapshotModel(db.Model):
    __tablename__ = "assessment_input_snapshots"

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
        unique=True,
        index=True,
    )

    weather_observed_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    weather_temperature = db.Column(
        db.Float,
        nullable=True,
    )

    weather_humidity = db.Column(
        db.Float,
        nullable=True,
    )

    weather_precipitation = db.Column(
        db.Float,
        nullable=True,
    )

    weather_wind_speed = db.Column(
        db.Float,
        nullable=True,
    )

    weather_soil_temperature = db.Column(
        db.Float,
        nullable=True,
    )

    weather_soil_temperature_6cm = db.Column(
        db.Float,
        nullable=True,
    )

    weather_soil_temperature_18cm = db.Column(
        db.Float,
        nullable=True,
    )

    soil_estimate_depth_cm = db.Column(
        db.Float,
        nullable=True,
    )

    soil_estimate_temperature = db.Column(
        db.Float,
        nullable=True,
    )

    soil_estimate_source_depths = db.Column(
        db.JSON,
        nullable=True,
    )

    soil_estimate_source_temperatures = db.Column(
        db.JSON,
        nullable=True,
    )

    soil_estimate_method = db.Column(
        db.String(50),
        nullable=True,
    )

    degree_days_base_temperature = db.Column(
        db.Float,
        nullable=True,
    )

    degree_days_total = db.Column(
        db.Float,
        nullable=True,
    )

    degree_days_period_start = db.Column(
        db.Date,
        nullable=True,
    )

    degree_days_period_end = db.Column(
        db.Date,
        nullable=True,
    )

    degree_days_method = db.Column(
        db.String(50),
        nullable=True,
    )

    degree_days_observations = db.Column(
        db.JSON,
        nullable=True,
    )

    saturation_deficit_mm_hg = db.Column(
        db.Float,
        nullable=True,
    )

    historical_observations = db.Column(
        db.JSON,
        nullable=True,
    )

    assessment = db.relationship(
        "AssessmentModel",
        back_populates="input_snapshot",
    )