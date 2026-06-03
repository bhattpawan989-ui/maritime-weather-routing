from fastapi import APIRouter

from app.schemas.risk import PredictRiskRequest, PredictRiskResponse
from app.services.risk.predictor import predict_risk

router = APIRouter(tags=["risk"])


@router.post("/predict-risk", response_model=PredictRiskResponse)
def predict_risk_endpoint(payload: PredictRiskRequest) -> PredictRiskResponse:
    return predict_risk(payload)
