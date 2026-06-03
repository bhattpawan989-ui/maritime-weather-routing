import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from geoalchemy2 import Geography
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RecommendationStatus

if TYPE_CHECKING:
    from app.models.voyage import Voyage


class RouteRecommendation(Base):
    __tablename__ = "route_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    voyage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("voyages.id", ondelete="CASCADE"), nullable=False
    )
    recommended_route = mapped_column(
        Geography(geometry_type="LINESTRING", srid=4326), nullable=False
    )
    extra_distance_nm: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    eta_difference_hours: Mapped[float] = mapped_column(
        Numeric(8, 2), nullable=False, default=0
    )
    fuel_difference_mt: Mapped[float] = mapped_column(
        Numeric(12, 4), nullable=False, default=0
    )
    fuel_difference_cost_usd: Mapped[float | None] = mapped_column(Numeric(14, 2))
    status: Mapped[RecommendationStatus] = mapped_column(
        Enum(RecommendationStatus, name="recommendation_status", create_type=False),
        nullable=False,
        default=RecommendationStatus.PENDING,
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    voyage: Mapped["Voyage"] = relationship(back_populates="recommendations")
