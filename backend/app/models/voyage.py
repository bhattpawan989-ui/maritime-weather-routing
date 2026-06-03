import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from geoalchemy2 import Geography
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import VoyageStatus

if TYPE_CHECKING:
    from app.models.fuel import FuelPrediction
    from app.models.laycan import LaycanAnalysis
    from app.models.recommendation import RouteRecommendation
    from app.models.vessel import Vessel
    from app.models.waypoint import RouteWaypoint


class Voyage(Base):
    __tablename__ = "voyages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vessel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vessels.id"), nullable=False
    )
    voyage_code: Mapped[str | None] = mapped_column(String(64))
    departure_port: Mapped[str] = mapped_column(String(128), nullable=False)
    destination_port: Mapped[str] = mapped_column(String(128), nullable=False)
    departure_point = mapped_column(Geography(geometry_type="POINT", srid=4326))
    destination_point = mapped_column(Geography(geometry_type="POINT", srid=4326))
    route_line = mapped_column(Geography(geometry_type="LINESTRING", srid=4326))
    laycan_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    laycan_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_eta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[VoyageStatus] = mapped_column(
        Enum(VoyageStatus, name="voyage_status", create_type=False),
        nullable=False,
        default=VoyageStatus.DRAFT,
    )
    total_distance_nm: Mapped[float | None] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    vessel: Mapped["Vessel"] = relationship(back_populates="voyages")
    waypoints: Mapped[list["RouteWaypoint"]] = relationship(
        back_populates="voyage", cascade="all, delete-orphan"
    )
    fuel_predictions: Mapped[list["FuelPrediction"]] = relationship(
        back_populates="voyage"
    )
    recommendations: Mapped[list["RouteRecommendation"]] = relationship(
        back_populates="voyage"
    )
    laycan_analyses: Mapped[list["LaycanAnalysis"]] = relationship(
        back_populates="voyage"
    )
