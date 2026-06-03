from fastapi import APIRouter

from app.schemas.speed import PredictSpeedRequest, PredictSpeedResponse
from app.services.speed.predictor import predict_speed

router = APIRouter(tags=["speed"])


@router.post("/predict-speed", response_model=PredictSpeedResponse)
def predict_speed_endpoint(payload: PredictSpeedRequest) -> PredictSpeedResponse:
    return predict_speed(payload)
