from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.services.reports_service import get_reports, create_report, add_report_feedback
from app.schemas.schemas import Report, ReportCreate, ReportFeedback

router = APIRouter(prefix="/api/reports", tags=["Community Reports"])

@router.get("", response_model=List[Dict[str, Any]])
def list_reports(
    category: Optional[str] = Query(None, description="road_hazard, lighting, sanitation, safety_concern, flooding, traffic_outage"),
    severity: Optional[str] = Query(None, description="low, medium, high, critical"),
    status: Optional[str] = Query(None, description="pending, under_review, verified"),
    search: Optional[str] = Query(None, description="Search in title or description"),
    lat: Optional[float] = Query(None, description="User latitude"),
    lng: Optional[float] = Query(None, description="User longitude"),
    radius_km: Optional[float] = Query(None, description="Radius filter in km")
):
    return get_reports(
        category=category,
        severity=severity,
        status=status,
        search=search,
        user_lat=lat,
        user_lng=lng,
        radius_km=radius_km
    )

@router.post("", response_model=Report, status_code=201)
def submit_report(payload: ReportCreate):
    return create_report(payload)

@router.post("/{report_id}/feedback")
def report_feedback(report_id: str, feedback: ReportFeedback):
    if feedback.action not in ["helpful", "duplicate"]:
        raise HTTPException(status_code=400, detail="Action must be 'helpful' or 'duplicate'")
    updated = add_report_feedback(report_id, feedback.action)
    if not updated:
        raise HTTPException(status_code=404, detail="Report not found")
    return updated
