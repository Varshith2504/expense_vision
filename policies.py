import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Policy, Claim
from backend.schemas import PolicyResponse, PolicyUpdate
from backend.services.policy_service import evaluate_policy_rules

router = APIRouter(prefix="/api/policies", tags=["Policies"])

@router.get("", response_model=PolicyResponse)
def get_policies(db: Session = Depends(get_db)):
    policy = db.query(Policy).first()
    if not policy:
        policy = Policy(intern_limit=3000.0, travel_cap=1500.0, it_budget=50000.0)
        db.add(policy)
        db.commit()
        db.refresh(policy)
    return policy.to_dict()

@router.put("", response_model=PolicyResponse)
def update_policies(payload: PolicyUpdate, db: Session = Depends(get_db)):
    policy = db.query(Policy).first()
    if not policy:
        policy = Policy()
        db.add(policy)

    policy.intern_limit = payload.internLimit
    policy.travel_cap = payload.travelCap
    policy.it_budget = payload.itBudget
    db.commit()
    db.refresh(policy)

    # Recalculate pending claims against updated policy rules
    pending_claims = db.query(Claim).filter(Claim.status == "Pending").all()
    for claim in pending_claims:
        is_tampered = claim.risk_level == "High" and "TAMPERED" in (claim.description or "")
        updated_checks, policy_failed = evaluate_policy_rules(
            claim.amount, claim.category, claim.merchant, claim.submitter, is_tampered, policy
        )
        claim.policy_checks_json = json.dumps(updated_checks)
        if policy_failed and claim.risk_level == "Low":
            claim.risk_level = "Medium"
            claim.anomaly_score = 0.45
        elif not policy_failed and claim.risk_level == "Medium":
            claim.risk_level = "Low"
            claim.anomaly_score = 0.15

    db.commit()
    return policy.to_dict()
