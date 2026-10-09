from fastapi import APIRouter
from datetime import datetime, timezone
from app.config import settings

router = APIRouter(prefix="/api/health", tags=["System Health"])

@router.get("")
def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "data_mode": settings.DATA_MODE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "sqlite_connected",
        "capabilities": [
            "places_catalog",
            "citizen_reports",
            "explainable_compare_engine",
            "ai_copilot",
            "smart_insights"
        ]
    }
