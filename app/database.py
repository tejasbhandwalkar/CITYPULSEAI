import sqlite3
import json
import math
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.seed_data import SEED_PLACES, SEED_REPORTS

DB_PATH = "citypulse.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on Earth in kilometers."""
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Places Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS places (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        neighborhood TEXT NOT NULL,
        city TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        rating REAL NOT NULL,
        review_count INTEGER NOT NULL,
        price_level TEXT NOT NULL,
        address TEXT NOT NULL,
        opening_hours TEXT NOT NULL,
        wheelchair_accessible INTEGER NOT NULL,
        image_url TEXT NOT NULL,
        description TEXT NOT NULL,
        tags TEXT NOT NULL,
        highlights TEXT NOT NULL,
        entry_cost TEXT NOT NULL,
        visit_duration TEXT NOT NULL,
        is_heritage INTEGER NOT NULL,
        data_source TEXT NOT NULL
    )
    """)
    
    # Reports Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        description TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        neighborhood TEXT NOT NULL,
        address TEXT NOT NULL,
        status TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        upvotes INTEGER NOT NULL DEFAULT 0,
        duplicate_flags INTEGER NOT NULL DEFAULT 0,
        image_url TEXT,
        voice_url TEXT,
        reporter_hash TEXT NOT NULL,
        data_source TEXT NOT NULL
    )
    """)

    conn.commit()

    # Seed places if empty
    cursor.execute("SELECT COUNT(*) FROM places")
    if cursor.fetchone()[0] == 0:
        for p in SEED_PLACES:
            cursor.execute("""
            INSERT INTO places (
                id, name, category, neighborhood, city, lat, lng, rating, review_count,
                price_level, address, opening_hours, wheelchair_accessible, image_url,
                description, tags, highlights, entry_cost, visit_duration, is_heritage, data_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["id"], p["name"], p["category"], p["neighborhood"], p["city"],
                p["lat"], p["lng"], p["rating"], p["review_count"], p["price_level"],
                p["address"], p["opening_hours"], 1 if p["wheelchair_accessible"] else 0,
                p["image_url"], p["description"], json.dumps(p["tags"]), json.dumps(p["highlights"]),
                p["entry_cost"], p["visit_duration"], 1 if p["is_heritage"] else 0, p["data_source"]
            ))

    # Seed reports if empty
    cursor.execute("SELECT COUNT(*) FROM reports")
    if cursor.fetchone()[0] == 0:
        for r in SEED_REPORTS:
            cursor.execute("""
            INSERT INTO reports (
                id, title, category, severity, description, lat, lng, neighborhood,
                address, status, timestamp, upvotes, duplicate_flags, image_url, voice_url,
                reporter_hash, data_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r["id"], r["title"], r["category"], r["severity"], r["description"],
                r["lat"], r["lng"], r["neighborhood"], r["address"], r["status"],
                r["timestamp"], r["upvotes"], r["duplicate_flags"], r["image_url"],
                r["voice_url"], r["reporter_hash"], r["data_source"]
            ))
            
    conn.commit()
    conn.close()
