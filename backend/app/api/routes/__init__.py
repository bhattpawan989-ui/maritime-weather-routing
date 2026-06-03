from fastapi import APIRouter

from app.api.routes import (
    analyze_route,
    calculate_cost,
    predict_fuel,
    predict_risk,
    predict_speed,
    recommend_route,
)

api_router = APIRouter()
api_router.include_router(analyze_route.router)
api_router.include_router(predict_risk.router)
api_router.include_router(predict_speed.router)
api_router.include_router(predict_fuel.router)
api_router.include_router(recommend_route.router)
api_router.include_router(calculate_cost.router)
