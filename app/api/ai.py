from fastapi import APIRouter
from app.schemas.schemas import AIQuery, AIResponse
from app.services.ai_service import handle_ai_query

router = APIRouter(prefix="/api/ai", tags=["CityPulse Copilot AI"])

@router.post("/recommend", response_model=AIResponse)
def get_ai_recommendations(query: AIQuery):
    return handle_ai_query(query)
