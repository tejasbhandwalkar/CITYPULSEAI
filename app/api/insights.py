from fastapi import APIRouter
from typing import Dict, Any
from app.services.insights_service import get_smart_insights

router = APIRouter(prefix="/api/insights", tags=["Smart City Insights"])

@router.get("", response_model=Dict[str, Any])
def fetch_city_insights():
    return get_smart_insights()
