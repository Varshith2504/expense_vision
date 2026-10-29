import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import CORS_ORIGINS, UPLOAD_DIR
from backend.database import engine, Base, SessionLocal
from backend.models import Policy
from backend.routers import claims, policies, twilio_webhook

# Initialize Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Expense Vision API",
    description="Backend service for OCR receipt processing, ELA image forensics, Isolation Forest ML fraud detection, and Twilio WhatsApp webhooks.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads static folder to serve original & ELA images
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include API Routers
app.include_router(claims.router)
app.include_router(policies.router)
app.include_router(twilio_webhook.router)

@app.on_event("startup")
def seed_default_policy():
    """Ensure default compliance policy exists on database initialization."""
    db = SessionLocal()
    try:
        if db.query(Policy).count() == 0:
            default_policy = Policy(
                intern_limit=3000.0,
                travel_cap=1500.0,
                it_budget=50000.0,
                tenant_id="TATA-CORP"
            )
            db.add(default_policy)
            db.commit()
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Expense Vision Python Backend API",
        "docs": "/docs",
        "endpoints": ["/api/claims", "/api/policies", "/api/webhook/whatsapp"]
    }

