from fastapi import APIRouter

from app.schemas.diversion import RecommendRouteRequest, RecommendRouteResponse
from app.services.diversion.engine import recommend_route

router = APIRouter(tags=["diversion"])


@router.post("/recommend-route", response_model=RecommendRouteResponse)
def recommend_route_endpoint(
    payload: RecommendRouteRequest,
) -> RecommendRouteResponse:
    return recommend_route(payload)
