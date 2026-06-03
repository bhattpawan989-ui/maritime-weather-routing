import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from geoalchemy2 import Geography
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.voyage import Voyage
    from app.models.weather import WeatherData, WeatherRisk


class RouteWaypoint(Base):
    __tablename__ = "route_waypoints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    voyage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("voyages.id", ondelete="CASCADE"), nullable=False
    )
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    location = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(128))
    eta_at_waypoint: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    vessel_heading_deg: Mapped[float | None] = mapped_column(Numeric(6, 2))
    distance_from_prev_nm: Mapped[float | None] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    voyage: Mapped["Voyage"] = relationship(back_populates="waypoints")
    weather_data: Mapped[list["WeatherData"]] = relationship(
        back_populates="waypoint", cascade="all, delete-orphan"
    )
    weather_risks: Mapped[list["WeatherRisk"]] = relationship(
        back_populates="waypoint", cascade="all, delete-orphan"
    )
