from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import DatabaseError
from app.schemas.route import AnalyzeRouteRequest, AnalyzeRouteResponse
from app.services.route.analyzer import analyze_route

router = APIRouter(tags=["route"])


@router.post("/analyze-route", response_model=AnalyzeRouteResponse)
def analyze_route_endpoint(
    payload: AnalyzeRouteRequest,
    db: Session = Depends(get_db),
) -> AnalyzeRouteResponse:
    try:
        session = db if payload.save_to_db else None
        return analyze_route(payload, session)
    except SQLAlchemyError as exc:
        if payload.save_to_db:
            db.rollback()
            raise DatabaseError(str(exc)) from exc
        raise
