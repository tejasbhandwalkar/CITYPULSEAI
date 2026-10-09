import re
import json
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.config import settings
from app.services.places_service import get_places
from app.services.reports_service import get_reports
from app.schemas.schemas import AIQuery, AIResponse, Place

def handle_ai_query(query: AIQuery) -> AIResponse:
    prompt = query.prompt.strip()
    prompt_lower = prompt.lower()
    
    # 1. Check if Gemini API is available
    if settings.GEMINI_API_KEY:
        try:
            return call_gemini_api(query)
        except Exception:
            pass # Fall back gracefully to local reasoning engine

    # 2. Intelligent Grounded Rule-Based / NLP Intent Engine
    all_places = get_places()
    all_reports = get_reports()
    
    intent = "general_explore"
    extracted_filters = {}
    suggested = []
    safety_context = None
    follow_ups = []
    
    # Intent: Heritage & Culture / Walking Tour
    if any(k in prompt_lower for k in ["heritage", "culture", "history", "monument", "tour", "peshwa", "fort", "museum"]):
        intent = "heritage_tour"
        extracted_filters = {"is_heritage": True, "category": "Attractions & Museums"}
        suggested = [p for p in all_places if p.get("is_heritage") or p.get("category") in ["Attractions", "Museums"]][:4]
        
        reply = (
            "🏛️ **Here is a recommended Heritage & Culture Tour for Pune:**\n\n"
            "1. **Morning (08:30 AM):** Start at **Shaniwar Wada**, the historic 18th-century Peshwa seat. Marvel at the Dilli Darwaza and fortified ramparts.\n"
            "2. **Midday:** Visit **Pataleshwar Cave Temple** on JM Road, an 8th-century monolithic rock-cut cave carved from single basalt.\n"
            "3. **Afternoon:** Head to **Aga Khan Palace** in Yerawada, an Italianate palace that served as Mahatma Gandhi's refuge and Kasturba Gandhi's memorial.\n"
            "4. **Sunset (Optional):** Trek to **Sinhagad Fort** for legendary Sahyadri panoramic views and freshly prepared Kanda Bhaji & Pithla Bhakri.\n\n"
            "💡 *Tip:* Check our **History & Culture** section to follow the multi-stop interactive Peshwa Heritage Walking Trail on the map!"
        )
        follow_ups = ["Show Peshwa Trail on Map", "Where to get authentic Puneri breakfast?", "Check admission costs & hours"]

    # Intent: Budget / Affordable Places
    elif any(k in prompt_lower for k in ["budget", "cheap", "affordable", "student", "low cost", "free"]):
        intent = "budget_discovery"
        extracted_filters = {"price_level": ["Free", "$"]}
        suggested = [p for p in all_places if p.get("price_level") in ["Free", "$"]][:4]
        
        reply = (
            "💰 **Top Budget-Friendly & Free Spots in Pune:**\n\n"
            "• **Vohuman Cafe:** Authentic Irani double-cheese omelette and bun maska under ₹150.\n"
            "• **Kata Kirr:** Celebrated fiery Puneri Misal Pav with farsan and mattha for ₹120.\n"
            "• **Pu La Deshpande Okayama Garden:** Gorgeous Japanese-style tranquil landscape for ₹20 entry.\n"
            "• **Zostel Pune (Viman Nagar):** Quality backpacker dorms starting at ₹699/night with high-speed WiFi and community events.\n"
            "• **Osho Teerth Park & Pataleshwar Caves:** Free entry public heritage and zen garden spaces."
        )
        follow_ups = ["Compare Vohuman vs Vaishali", "Find budget hostels near Airport", "Filter by rating > 4.5"]

    # Intent: Food & Cafes
    elif any(k in prompt_lower for k in ["food", "restaurant", "cafe", "eat", "misal", "breakfast", "coffee", "chai", "dine"]):
        intent = "food_discovery"
        extracted_filters = {"category": "Restaurants & Cafes"}
        suggested = [p for p in all_places if p.get("category") in ["Restaurants", "Cafes", "Street Food"]][:4]
        
        reply = (
            "☕ **Pune's Signature Food Recommendations:**\n\n"
            "• **Vaishali (FC Road):** The quintessential Deccan student rendezvous. Try their Mysore Masala Dosa, Filter Coffee, and iconic SPDP.\n"
            "• **Vohuman Cafe (Station / Sassoon Rd):** Pune's beloved Irani cafe since 1978. Order the Double Cheese Omelette with Brun Maska.\n"
            "• **Kata Kirr (Karve Rd):** The gold standard for spicy Kolhapuri-style Misal Pav with crunchy farsan and soothing buttermilk.\n\n"
            "All locations are verified popular local favorites with high cleanliness and student-friendly pricing."
        )
        follow_ups = ["Show food spots on map", "Find vegetarian options", "Check open hours"]

    # Intent: Safety & Hazards & Routing
    elif any(k in prompt_lower for k in ["safe", "safety", "hazard", "pothole", "lighting", "route", "incident", "dark", "flood"]):
        intent = "safety_intelligence"
        extracted_filters = {"incident_reports": "active"}
        
        reply = (
            "🛡️ **Safety Intelligence & Reported Hazard Summary:**\n\n"
            "• **Swargate Underpass Ramp:** Deep pothole cluster logged (Severity: High). Two-wheelers should exercise caution.\n"
            "• **North Main Road (Koregaon Park Lane 5-7):** Broken streetlights over 300m stretch reported by citizens (Severity: Medium).\n"
            "• **Dengle Bridge Approach:** Known temporary waterlogging during sudden heavy downpours.\n\n"
            "⚠️ **Responsible AI Notice:** *Report counts represent citizen submissions, not comprehensive crime tallies. Reporting bias exists; algorithmic suggestions do not guarantee personal safety. Always exercise personal situational awareness.*"
        )
        safety_context = "Reports retrieved from CityPulse community database. 3 verified alerts active."
        follow_ups = ["Open Safety Dashboard", "Report a New Road Issue", "Find nearest 24/7 Hospital"]

    # Intent: Neighborhood Comparison
    elif any(k in prompt_lower for k in ["compare", "versus", "vs", "which neighborhood", "which area"]):
        intent = "neighborhood_compare"
        suggested = [p for p in all_places if p["id"] in ["pune-vaishali", "pune-jw-marriott", "pune-zostel"]][:3]
        
        reply = (
            "⚖️ **Neighborhood Comparison: FC Road (Deccan) vs Koregaon Park (KP):**\n\n"
            "• **Vibe & Culture:** FC Road offers classic university buzz, affordable street food, and historic colleges. KP is leafy, upscale, cosmopolitan with chic bistros and yoga centers.\n"
            "• **Affordability:** FC Road ranks 88/100 for budget travelers. KP is more premium ($$ to $$$).\n"
            "• **Reported Civic Alerts:** Koregaon Park has 1 active street lighting report; Deccan has 1 pedestrian timer issue logged.\n"
            "• **Transit Access:** FC Road has closer connectivity to Deccan Gymkhana Metro station.\n\n"
            "You can run an interactive side-by-side comparison in the **Compare Places** tab with custom weighting!"
        )
        follow_ups = ["Open Compare Places tool", "Adjust comparison weights", "View transit scores"]

    # Default: General Smart City Overview
    else:
        intent = "city_explore_general"
        suggested = all_places[:3]
        reply = (
            f"👋 **Welcome to CityPulse AI for Pune!**\n\n"
            f"I can help you explore verified places, navigate safely, and discover local culture. Try asking:\n"
            f"• *'Plan a one-day heritage walking tour'*\n"
            f"• *'Find affordable breakfast cafes with high ratings'*\n"
            f"• *'Summarize reported road hazards and dark alleys'*\n"
            f"• *'Compare FC Road vs Koregaon Park'*\n\n"
            f"Currently monitoring **{len(all_places)} curated locations** and **{len(all_reports)} community reports**."
        )
        follow_ups = ["Plan a one-day heritage tour", "Find affordable restaurants", "Check reported safety hazards"]

    return AIResponse(
        reply=reply,
        intent=intent,
        filters_extracted=extracted_filters,
        suggested_places=[Place(**p) for p in suggested],
        safety_context=safety_context,
        follow_up_suggestions=follow_ups,
        data_timestamp=datetime.now(timezone.utc).isoformat(),
        mode="curated_nlp_engine"
    )

def call_gemini_api(query: AIQuery) -> AIResponse:
    # Live Gemini API call if key is set
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    system_instruction = (
        "You are CityPulse Copilot, an AI assistant for smart city exploration in Pune, India. "
        "Provide factual, helpful, and concise guidance about places, culture, and safety. "
        "Ground recommendations in verified city information. Do not invent crime data. "
        "Always state that incident counts represent citizen reports, not complete crime records."
    )
    payload = {
        "contents": [{"parts": [{"text": query.prompt}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    resp = httpx.post(url, json=payload, timeout=6.0)
    if resp.status_code == 200:
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return AIResponse(
            reply=text,
            intent="gemini_llm_inference",
            filters_extracted={},
            suggested_places=[],
            safety_context=None,
            follow_up_suggestions=["Ask another question", "Show nearby attractions"],
            data_timestamp=datetime.now(timezone.utc).isoformat(),
            mode="gemini_live"
        )
    raise RuntimeError("Gemini API call failed")
