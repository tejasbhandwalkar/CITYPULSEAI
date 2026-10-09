import uuid
import random
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.database import get_connection, haversine_distance
from app.schemas.schemas import Report, ReportCreate

def row_to_report(row) -> Report:
    return Report(
        id=row["id"],
        title=row["title"],
        category=row["category"],
        severity=row["severity"],
        description=row["description"],
        lat=row["lat"],
        lng=row["lng"],
        neighborhood=row["neighborhood"],
        address=row["address"],
        status=row["status"],
        timestamp=row["timestamp"],
        upvotes=row["upvotes"],
        duplicate_flags=row["duplicate_flags"],
        image_url=row["image_url"],
        voice_url=row["voice_url"],
        reporter_hash=row["reporter_hash"],
        data_source=row["data_source"]
    )

def get_reports(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    radius_km: Optional[float] = None
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    reports = [row_to_report(r) for r in rows]
    results = []

    for rep in reports:
        if category and category.lower() != "all" and rep.category.lower() != category.lower():
            continue
        if severity and severity.lower() != "all" and rep.severity.lower() != severity.lower():
            continue
        if status and status.lower() != "all" and rep.status.lower() != status.lower():
            continue
        if search:
            q = search.lower()
            if q not in rep.title.lower() and q not in rep.description.lower() and q not in rep.neighborhood.lower():
                continue

        dist = None
        if user_lat is not None and user_lng is not None:
            dist = round(haversine_distance(user_lat, user_lng, rep.lat, rep.lng), 2)
            if radius_km and dist > radius_km:
                continue

        r_dict = rep.model_dump()
        r_dict["distance_km"] = dist
        results.append(r_dict)

    return results

def create_report(payload: ReportCreate) -> Report:
    conn = get_connection()
    cursor = conn.cursor()
    
    report_id = f"rep-{uuid.uuid4().hex[:8]}"
    reporter_hash = f"Citizen #{random.randint(1000, 9999)}"
    now_iso = datetime.now(timezone.utc).isoformat()
    
    neighborhood = payload.neighborhood or "Pune Central"
    address = payload.address or f"Coordinates: {payload.lat:.4f}, {payload.lng:.4f}"
    status = "pending"
    data_source = "community_submission"

    cursor.execute("""
    INSERT INTO reports (
        id, title, category, severity, description, lat, lng, neighborhood,
        address, status, timestamp, upvotes, duplicate_flags, image_url,
        voice_url, reporter_hash, data_source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report_id, payload.title, payload.category, payload.severity,
        payload.description, payload.lat, payload.lng, neighborhood,
        address, status, now_iso, 0, 0, payload.image_url,
        payload.voice_url, reporter_hash, data_source
    ))
    
    conn.commit()
    conn.close()

    return Report(
        id=report_id,
        title=payload.title,
        category=payload.category,
        severity=payload.severity,
        description=payload.description,
        lat=payload.lat,
        lng=payload.lng,
        neighborhood=neighborhood,
        address=address,
        status=status,
        timestamp=now_iso,
        upvotes=0,
        duplicate_flags=0,
        image_url=payload.image_url,
        voice_url=payload.voice_url,
        reporter_hash=reporter_hash,
        data_source=data_source
    )

def add_report_feedback(report_id: str, action: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    if action == "helpful":
        cursor.execute("UPDATE reports SET upvotes = upvotes + 1 WHERE id = ?", (report_id,))
    elif action == "duplicate":
        cursor.execute("UPDATE reports SET duplicate_flags = duplicate_flags + 1 WHERE id = ?", (report_id,))

    conn.commit()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    updated_row = cursor.fetchone()
    conn.close()
    return row_to_report(updated_row).model_dump()
