from fastapi import APIRouter

from app.schemas.fuel import PredictFuelRequest, PredictFuelResponse
from app.services.fuel.predictor import predict_fuel

router = APIRouter(tags=["fuel"])


@router.post("/predict-fuel", response_model=PredictFuelResponse)
def predict_fuel_endpoint(payload: PredictFuelRequest) -> PredictFuelResponse:
    return predict_fuel(payload)
