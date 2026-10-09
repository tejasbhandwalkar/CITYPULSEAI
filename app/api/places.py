from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.services.places_service import get_places, get_place_by_id
from app.schemas.schemas import Place

router = APIRouter(prefix="/api/places", tags=["Places"])

@router.get("", response_model=List[Dict[str, Any]])
def list_places(
    search: Optional[str] = Query(None, description="Search term in name, description, tags"),
    category: Optional[str] = Query(None, description="Category filter"),
    neighborhood: Optional[str] = Query(None, description="Neighborhood filter"),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0, description="Minimum rating"),
    price_level: Optional[str] = Query(None, description="Price level: Free, $, $$, $$$"),
    accessible_only: Optional[bool] = Query(None, description="Wheelchair accessible filter"),
    heritage_only: Optional[bool] = Query(None, description="Heritage only filter"),
    lat: Optional[float] = Query(None, description="User latitude"),
    lng: Optional[float] = Query(None, description="User longitude"),
    max_distance_km: Optional[float] = Query(None, description="Max radius in km"),
    sort_by: Optional[str] = Query("relevance", description="relevance, rating, distance, price_asc, reviews")
):
    return get_places(
        search=search,
        category=category,
        neighborhood=neighborhood,
        min_rating=min_rating,
        price_level=price_level,
        accessible_only=accessible_only,
        heritage_only=heritage_only,
        user_lat=lat,
        user_lng=lng,
        max_distance_km=max_distance_km,
        sort_by=sort_by
    )

@router.get("/{place_id}", response_model=Place)
def retrieve_place(place_id: str):
    place = get_place_by_id(place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place
