import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.voyage import Voyage
    from app.models.waypoint import RouteWaypoint


class FuelPrediction(Base):
    __tablename__ = "fuel_predictions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    voyage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("voyages.id", ondelete="CASCADE"), nullable=False
    )
    waypoint_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("route_waypoints.id", ondelete="SET NULL")
    )
    stw_knots: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    effective_sog_knots: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    distance_nm: Mapped[float | None] = mapped_column(Numeric(10, 2))
    fuel_consumption_mt: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    fuel_cost_usd: Mapped[float | None] = mapped_column(Numeric(14, 2))
    delay_hours: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=0)
    predicted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    voyage: Mapped["Voyage"] = relationship(back_populates="fuel_predictions")
    waypoint: Mapped["RouteWaypoint | None"] = relationship()
