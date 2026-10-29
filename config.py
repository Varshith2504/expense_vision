import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
ELA_DIR = UPLOAD_DIR / "ela"

# Create upload directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ELA_DIR.mkdir(parents=True, exist_ok=True)

# Database URL - SQLite default for zero-setup local execution, supports MySQL via env
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/expense_vision.db")

# Twilio WhatsApp Integration Config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# CORS Origins
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
