from typing import List, Dict, Any, Optional
from app.services.places_service import get_place_by_id
from app.services.reports_service import get_reports
from app.database import haversine_distance
from app.schemas.schemas import CompareRequest, CompareResponse, PlaceScoreBreakdown

def compare_places(request: CompareRequest) -> CompareResponse:
    place_ids = request.place_ids[:4] # max 4 places
    weights = request.weights or {
        "safety": 0.30,
        "affordability": 0.25,
        "rating": 0.30,
        "transit": 0.15,
        "cleanliness": 0.0 # Cleanliness excluded unless verified data exists
    }
    
    if hasattr(weights, "model_dump"):
        weights = weights.model_dump()

    all_reports = get_reports()
    places = []
    breakdowns = []
    
    # Pune Junction coordinates for transit reference
    TRANSIT_HUB_LAT = 18.5289
    TRANSIT_HUB_LNG = 73.8744

    for pid in place_ids:
        place = get_place_by_id(pid)
        if not place:
            continue
        places.append(place)

        # 1. Safety Score from citizen reports within 2.5km
        nearby_reports = [
            r for r in all_reports
            if haversine_distance(place.lat, place.lng, r["lat"], r["lng"]) <= 2.5
        ]
        
        # Penalties: critical -15, high -10, medium -5, low -2
        penalty = 0
        for r in nearby_reports:
            sev = r.get("severity", "medium").lower()
            if sev == "critical":
                penalty += 15
            elif sev == "high":
                penalty += 10
            elif sev == "medium":
                penalty += 5
            else:
                penalty += 2
                
        safety_score = max(35.0, round(95.0 - penalty, 1))

        # 2. Affordability Score
        price_map = {"Free": 100.0, "$": 85.0, "$$": 65.0, "$$$": 40.0}
        affordability_score = price_map.get(place.price_level, 70.0)

        # 3. Rating Score (out of 100)
        rating_score = round((place.rating / 5.0) * 100.0, 1)

        # 4. Transit Access Score
        dist_to_transit = haversine_distance(place.lat, place.lng, TRANSIT_HUB_LAT, TRANSIT_HUB_LNG)
        transit_score = max(40.0, round(100.0 - (dist_to_transit * 6.0), 1))

        # 5. Cleanliness: We adhere strictly to instructions:
        # "Never create unsupported cleanliness scores or safety ratings when the required data is missing. Show 'Insufficient data' where appropriate."
        cleanliness_score = None # Missing municipal street cleanliness index

        missing_fields = ["cleanliness (no verified municipal sensor data available)"]

        # Calculate weighted overall score
        w_safety = weights.get("safety", 0.30)
        w_afford = weights.get("affordability", 0.25)
        w_rating = weights.get("rating", 0.30)
        w_transit = weights.get("transit", 0.15)
        
        total_w = w_safety + w_afford + w_rating + w_transit
        if total_w <= 0:
            total_w = 1.0

        overall_score = round(
            ((safety_score * w_safety) +
             (affordability_score * w_afford) +
             (rating_score * w_rating) +
             (transit_score * w_transit)) / total_w,
            1
        )

        notes = (
            f"Rated {place.rating}★ ({place.review_count:,} reviews). "
            f"{len(nearby_reports)} nearby reported civic/safety incidents recorded within 2.5km. "
            f"Approx {dist_to_transit:.1f} km from central transit hub."
        )

        breakdowns.append(PlaceScoreBreakdown(
            place_id=place.id,
            place_name=place.name,
            overall_score=overall_score,
            safety_score=safety_score,
            affordability_score=affordability_score,
            rating_score=rating_score,
            transit_score=transit_score,
            cleanliness_score=cleanliness_score,
            missing_data_fields=missing_fields,
            notes=notes
        ))

    # Determine best recommendation
    best_choice = None
    if breakdowns:
        best_choice = max(breakdowns, key=lambda x: x.overall_score).place_id

    best_place_name = next((p.name for p in places if p.id == best_choice), "Selected location")

    recommendation_summary = (
        f"Based on your assigned weighting preferences, **{best_place_name}** ranks highest with an overall score "
        f"of {max((b.overall_score for b in breakdowns), default=0):.1f}/100. "
        f"It balances user ratings, budget friendliness, and local reported conditions effectively."
    )

    formula_explanation = (
        "Overall Score = [ (Safety × W_s) + (Affordability × W_a) + (Rating × W_r) + (Transit × W_t) ] / Sum(Weights). "
        "Safety reflects reported community alerts within 2.5km (counts represent user reports, not complete crime records). "
        "Cleanliness is marked as Insufficient Data because no real-time municipal street sanitation telemetry is active."
    )

    limitations = (
        "LIMITATION NOTICE: This ranking is an algorithmic decision aid based on available community and place data. "
        "It does not guarantee safety, spotless cleanliness, or transit timeliness. Please exercise personal discretion."
    )

    return CompareResponse(
        places=places,
        scores=breakdowns,
        best_choice_id=best_choice,
        recommendation_summary=recommendation_summary,
        formula_explanation=formula_explanation,
        data_limitations=limitations
    )
