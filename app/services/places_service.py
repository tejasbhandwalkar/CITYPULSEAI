import json
from typing import List, Optional, Dict, Any
from app.database import get_connection, haversine_distance
from app.schemas.schemas import Place

def row_to_place(row) -> Place:
    return Place(
        id=row["id"],
        name=row["name"],
        category=row["category"],
        neighborhood=row["neighborhood"],
        city=row["city"],
        lat=row["lat"],
        lng=row["lng"],
        rating=row["rating"],
        review_count=row["review_count"],
        price_level=row["price_level"],
        address=row["address"],
        opening_hours=row["opening_hours"],
        wheelchair_accessible=bool(row["wheelchair_accessible"]),
        image_url=row["image_url"],
        description=row["description"],
        tags=json.loads(row["tags"]) if isinstance(row["tags"], str) else row["tags"],
        highlights=json.loads(row["highlights"]) if isinstance(row["highlights"], str) else row["highlights"],
        entry_cost=row["entry_cost"],
        visit_duration=row["visit_duration"],
        is_heritage=bool(row["is_heritage"]),
        data_source=row["data_source"]
    )

def get_places(
    search: Optional[str] = None,
    category: Optional[str] = None,
    neighborhood: Optional[str] = None,
    min_rating: Optional[float] = None,
    price_level: Optional[str] = None,
    accessible_only: Optional[bool] = None,
    heritage_only: Optional[bool] = None,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    max_distance_km: Optional[float] = None,
    sort_by: Optional[str] = "relevance"  # relevance, rating, distance, price_asc
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM places")
    rows = cursor.fetchall()
    conn.close()

    places = [row_to_place(r) for r in rows]
    results = []

    for p in places:
        # Filter category
        if category and category.lower() != "all" and p.category.lower() != category.lower():
            continue
        
        # Filter neighborhood
        if neighborhood and neighborhood.lower() not in p.neighborhood.lower():
            continue

        # Filter search keyword
        if search:
            query = search.lower()
            in_name = query in p.name.lower()
            in_desc = query in p.description.lower()
            in_neigh = query in p.neighborhood.lower()
            in_tags = any(query in t.lower() for t in p.tags)
            if not (in_name or in_desc or in_neigh or in_tags):
                continue

        # Filter rating
        if min_rating and p.rating < min_rating:
            continue

        # Filter price level
        if price_level and price_level.lower() != "all" and p.price_level != price_level:
            continue

        # Filter accessibility
        if accessible_only and not p.wheelchair_accessible:
            continue

        # Filter heritage
        if heritage_only and not p.is_heritage:
            continue

        # Distance calculation
        dist = None
        if user_lat is not None and user_lng is not None:
            dist = round(haversine_distance(user_lat, user_lng, p.lat, p.lng), 2)
            if max_distance_km and dist > max_distance_km:
                continue

        p_dict = p.model_dump()
        p_dict["distance_km"] = dist
        results.append(p_dict)

    # Sorting
    if sort_by == "rating":
        results.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "distance" and user_lat is not None and user_lng is not None:
        results.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"] or 9999))
    elif sort_by == "price_asc":
        price_order = {"Free": 0, "$": 1, "$$": 2, "$$$": 3}
        results.sort(key=lambda x: price_order.get(x["price_level"], 2))
    elif sort_by == "reviews":
        results.sort(key=lambda x: x["review_count"], reverse=True)

    return results

def get_place_by_id(place_id: str) -> Optional[Place]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM places WHERE id = ?", (place_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row_to_place(row)
    return None
