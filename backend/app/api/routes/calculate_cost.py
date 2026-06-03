from fastapi import APIRouter

from app.schemas.cost import CalculateCostRequest, CalculateCostResponse
from app.services.cost.engine import calculate_cost

router = APIRouter(tags=["cost"])


@router.post("/calculate-cost", response_model=CalculateCostResponse)
def calculate_cost_endpoint(payload: CalculateCostRequest) -> CalculateCostResponse:
    return calculate_cost(payload)
