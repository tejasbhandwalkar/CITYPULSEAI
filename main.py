from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api import places, reports, compare, insights, ai, health

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CityPulse AI — Smart City Exploration & Intelligence Platform Backend API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to ensure database is created and seeded
@app.on_event("startup")
def on_startup():
    init_db()

# Register API Routers
app.include_router(health.router)
app.include_router(places.router)
app.include_router(reports.router)
app.include_router(compare.router)
app.include_router(insights.router)
app.include_router(ai.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to CityPulse AI API",
        "docs": "/docs",
        "health": "/api/health",
        "city": "Pune, India"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
