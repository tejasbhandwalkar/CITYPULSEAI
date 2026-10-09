from fastapi import APIRouter, HTTPException
from app.services.compare_service import compare_places
from app.schemas.schemas import CompareRequest, CompareResponse

router = APIRouter(prefix="/api/compare", tags=["Compare Places"])

@router.post("", response_model=CompareResponse)
def compare_selected_places(payload: CompareRequest):
    if not payload.place_ids:
        raise HTTPException(status_code=400, detail="At least one place ID must be provided")
    return compare_places(payload)
