import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RiskLevel

if TYPE_CHECKING:
    from app.models.waypoint import RouteWaypoint


class WeatherData(Base):
    __tablename__ = "weather_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    waypoint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("route_waypoints.id", ondelete="CASCADE"),
        nullable=False,
    )
    wind_speed_knots: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    wind_direction_deg: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    wave_height_m: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    current_speed_knots: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    current_direction_deg: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    forecast_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    data_source: Mapped[str] = mapped_column(String(64), nullable=False, default="synthetic")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    waypoint: Mapped["RouteWaypoint"] = relationship(back_populates="weather_data")


class WeatherRisk(Base):
    __tablename__ = "weather_risk"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    waypoint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("route_waypoints.id", ondelete="CASCADE"),
        nullable=False,
    )
    risk_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level", create_type=False), nullable=False
    )
    relative_heading_deg: Mapped[float | None] = mapped_column(Numeric(6, 2))
    model_version: Mapped[str | None] = mapped_column(String(32))
    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    waypoint: Mapped["RouteWaypoint"] = relationship(back_populates="weather_risks")
