import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "CityPulse AI"

def test_list_places():
    response = client.get("/api/places")
    assert response.status_code == 200
    places = response.json()
    assert len(places) > 0
    first = places[0]
    assert "name" in first
    assert "lat" in first
    assert "lng" in first

def test_filter_places_category():
    response = client.get("/api/places?category=Attractions")
    assert response.status_code == 200
    places = response.json()
    for p in places:
        assert p["category"].lower() == "attractions"

def test_submit_report_and_feedback():
    payload = {
        "title": "Loose Paver Blocks on Sidewalk",
        "category": "road_hazard",
        "severity": "medium",
        "description": "Trip hazard near main avenue bus shelter. Several loose tiles causing tripping.",
        "lat": 18.5204,
        "lng": 73.8567,
        "neighborhood": "Central Pune",
        "address": "Laxmi Road Corner"
    }
    response = client.post("/api/reports", json=payload)
    assert response.status_code == 201
    report = response.json()
    assert report["title"] == payload["title"]
    assert report["status"] == "pending"
    assert "Citizen #" in report["reporter_hash"]

    # Test feedback (upvote)
    rep_id = report["id"]
    fb_resp = client.post(f"/api/reports/{rep_id}/feedback", json={"action": "helpful"})
    assert fb_resp.status_code == 200
    assert fb_resp.json()["upvotes"] == 1

def test_compare_places():
    payload = {
        "place_ids": ["pune-shaniwar-wada", "pune-vaishali"],
        "weights": {
            "safety": 0.3,
            "affordability": 0.3,
            "rating": 0.2,
            "transit": 0.2,
            "cleanliness": 0.0
        }
    }
    response = client.post("/api/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["places"]) == 2
    assert len(data["scores"]) == 2
    assert data["best_choice_id"] is not None
    assert "formula_explanation" in data

def test_ai_recommend_endpoint():
    payload = {
        "prompt": "Find affordable breakfast and cafes in Pune",
        "city": "Pune"
    }
    response = client.post("/api/ai/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["follow_up_suggestions"]) > 0
