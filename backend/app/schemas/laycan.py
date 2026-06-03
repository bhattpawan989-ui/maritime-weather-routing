from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class LaycanInput(BaseModel):
    laycan_start: datetime
    laycan_end: datetime
    eta: datetime

    @model_validator(mode="after")
    def validate_window(self) -> "LaycanInput":
        if self.laycan_end < self.laycan_start:
            raise ValueError("laycan_end must be on or after laycan_start")
        return self


class LaycanAnalysisResult(BaseModel):
    laycan_risk_pct: float = Field(..., ge=0, le=100)
    missed_laycan_warning: bool
