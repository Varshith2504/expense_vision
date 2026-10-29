import json
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, DateTime
from backend.database import Base

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, index=True)
    submitter = Column(String, nullable=False)
    department = Column(String, nullable=False)
    merchant = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)
    status = Column(String, default="Pending") # Pending, Approved, Rejected
    risk_level = Column(String, default="Low") # Low, Medium, High
    anomaly_score = Column(Float, default=0.15)
    description = Column(Text, nullable=True)
    original_image_path = Column(String, nullable=True)
    ela_image_path = Column(String, nullable=True)
    policy_checks_json = Column(Text, nullable=True) # Stored JSON string
    ocr_data_json = Column(Text, nullable=True) # Stored JSON string
    tenant_id = Column(String, default="TATA-CORP")
    telegram_chat_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        policy_checks = {}
        if self.policy_checks_json:
            try:
                policy_checks = json.loads(self.policy_checks_json)
            except Exception:
                policy_checks = {}
                
        ocr_data = {}
        if self.ocr_data_json:
            try:
                ocr_data = json.loads(self.ocr_data_json)
            except Exception:
                ocr_data = {}

        return {
            "id": self.id,
            "submitter": self.submitter,
            "department": self.department,
            "merchant": self.merchant,
            "category": self.category,
            "amount": self.amount,
            "date": self.date,
            "status": self.status,
            "riskLevel": self.risk_level,
            "anomalyScore": self.anomaly_score,
            "description": self.description,
            "originalImagePath": self.original_image_path,
            "elaImagePath": self.ela_image_path,
            "policyChecks": policy_checks,
            "ocrData": ocr_data,
            "tenantId": self.tenant_id,
            "telegramChatId": self.telegram_chat_id,
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    intern_limit = Column(Float, default=3000.0)
    travel_cap = Column(Float, default=1500.0)
    it_budget = Column(Float, default=50000.0)
    tenant_id = Column(String, default="TATA-CORP")

    def to_dict(self):
        return {
            "internLimit": self.intern_limit,
            "travelCap": self.travel_cap,
            "itBudget": self.it_budget,
            "tenantId": self.tenant_id
        }

