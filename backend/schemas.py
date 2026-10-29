from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class ClaimCreate(BaseModel):
    submitter: str
    department: str
    merchant: str
    category: str
    amount: float
    date: Optional[str] = None
    description: Optional[str] = None
    is_tampered: Optional[bool] = False

class ClaimResponse(BaseModel):
    id: str
    submitter: str
    department: str
    merchant: str
    category: str
    amount: float
    date: str
    status: str
    riskLevel: str
    anomalyScore: float
    description: Optional[str] = None
    originalImagePath: Optional[str] = None
    elaImagePath: Optional[str] = None
    policyChecks: Optional[Dict[str, Any]] = None
    ocrData: Optional[Dict[str, Any]] = None
    tenantId: Optional[str] = "TATA-CORP"
    telegramChatId: Optional[str] = None
    createdAt: Optional[str] = None

class PolicyUpdate(BaseModel):
    internLimit: float
    travelCap: float
    itBudget: float

class PolicyResponse(BaseModel):
    internLimit: float
    travelCap: float
    itBudget: float
    tenantId: str

class StatsResponse(BaseModel):
    totalApproved: float
    pendingCount: int
    highRiskCount: int
    policyViolationsCount: int

