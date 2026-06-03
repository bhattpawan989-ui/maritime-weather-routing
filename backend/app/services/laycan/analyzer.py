from app.schemas.laycan import LaycanAnalysisResult, LaycanInput


def analyze_laycan(payload: LaycanInput) -> LaycanAnalysisResult:
    window_hours = (payload.laycan_end - payload.laycan_start).total_seconds() / 3600
    if payload.eta < payload.laycan_start:
        hours_out = (payload.laycan_start - payload.eta).total_seconds() / 3600
    elif payload.eta > payload.laycan_end:
        hours_out = (payload.eta - payload.laycan_end).total_seconds() / 3600
    else:
        hours_out = 0.0

    missed = hours_out > 0
    if window_hours <= 0:
        risk_pct = 100.0 if missed else 0.0
    else:
        risk_pct = min(100.0, (hours_out / window_hours) * 100.0)

    return LaycanAnalysisResult(
        laycan_risk_pct=round(risk_pct, 2),
        missed_laycan_warning=missed,
    )
