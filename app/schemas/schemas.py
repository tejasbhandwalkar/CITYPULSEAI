from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PlaceBase(BaseModel):
    name: str
    category: str
    neighborhood: str
    city: str = "Pune"
    lat: float
    lng: float
    rating: float = Field(..., ge=1.0, le=5.0)
    review_count: int = 0
    price_level: str = "$"  # $, $$, $$$, Free
    address: str
    opening_hours: str = "09:00 AM - 09:00 PM"
    wheelchair_accessible: bool = True
    image_url: str
    description: str
    tags: List[str] = []
    highlights: List[str] = []
    entry_cost: str = "Free"
    visit_duration: str = "1-2 hours"
    is_heritage: bool = False
    data_source: str = "curated_seed"

class Place(PlaceBase):
    id: str

class ReportCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120)
    category: str  # e.g., 'road_hazard', 'lighting', 'sanitation', 'safety_concern', 'flooding', 'traffic_outage'
    severity: str = "medium"  # low, medium, high, critical
    description: str = Field(..., min_length=10, max_length=1000)
    lat: float
    lng: float
    neighborhood: Optional[str] = "Pune Center"
    address: Optional[str] = "Pune, Maharashtra"
    image_url: Optional[str] = None
    voice_url: Optional[str] = None

class ReportFeedback(BaseModel):
    action: str  # 'helpful' or 'duplicate'

class Report(BaseModel):
    id: str
    title: str
    category: str
    severity: str
    description: str
    lat: float
    lng: float
    neighborhood: str
    address: str
    status: str = "pending"  # pending, under_review, verified
    timestamp: str
    upvotes: int = 0
    duplicate_flags: int = 0
    image_url: Optional[str] = None
    voice_url: Optional[str] = None
    reporter_hash: str  # Anonymized reporter hash, e.g. "Citizen #4921"
    data_source: str = "community_submission"

class CompareWeights(BaseModel):
    safety: float = 0.25
    affordability: float = 0.25
    rating: float = 0.25
    transit: float = 0.15
    cleanliness: float = 0.10

class CompareRequest(BaseModel):
    place_ids: List[str]
    weights: Optional[CompareWeights] = None

class PlaceScoreBreakdown(BaseModel):
    place_id: str
    place_name: str
    overall_score: float
    safety_score: Optional[float] = None
    affordability_score: Optional[float] = None
    rating_score: Optional[float] = None
    transit_score: Optional[float] = None
    cleanliness_score: Optional[float] = None
    missing_data_fields: List[str] = []
    notes: str

class CompareResponse(BaseModel):
    places: List[Place]
    scores: List[PlaceScoreBreakdown]
    best_choice_id: Optional[str] = None
    recommendation_summary: str
    formula_explanation: str
    data_limitations: str

class AIQuery(BaseModel):
    prompt: str
    city: str = "Pune"
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None

class AIResponse(BaseModel):
    reply: str
    intent: str
    filters_extracted: Dict[str, Any] = {}
    suggested_places: List[Place] = []
    safety_context: Optional[str] = None
    follow_up_suggestions: List[str] = []
    data_timestamp: str
    mode: str = "curated_reasoning"
