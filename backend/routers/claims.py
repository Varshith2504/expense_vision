import os
import json
import uuid
import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Claim, Policy
from backend.schemas import ClaimResponse, ClaimCreate, StatsResponse
from backend.config import UPLOAD_DIR
from backend.services.ela_service import perform_ela_analysis
from backend.services.ocr_service import parse_receipt_ocr
from backend.services.fraud_service import calculate_fraud_anomaly_score
from backend.services.policy_service import evaluate_policy_rules
from backend.services.telegram_service import send_telegram_message

router = APIRouter(prefix="/api/claims", tags=["Claims"])

@router.get("", response_model=List[ClaimResponse])
def get_claims(
    status: Optional[str] = Query(None),
    risk: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Claim)
    if status and status != "All":
        query = query.filter(Claim.status == status)
    if risk and risk != "All":
        query = query.filter(Claim.risk_level == risk)
    if search:
        search_pattern = f"%{search.lower()}%"
        query = query.filter(
            (Claim.submitter.ilike(search_pattern)) |
            (Claim.merchant.ilike(search_pattern)) |
            (Claim.id.ilike(search_pattern))
        )
    claims = query.order_by(Claim.created_at.desc()).all()
    return [c.to_dict() for c in claims]

@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    claims = db.query(Claim).all()
    
    total_approved = sum(c.amount for c in claims if c.status == "Approved")
    pending_count = sum(1 for c in claims if c.status == "Pending")
    high_risk_count = sum(1 for c in claims if c.risk_level == "High" and c.status == "Pending")
    
    policy_violations_count = 0
    for c in claims:
        if c.status == "Pending" and c.policy_checks_json:
            try:
                checks = json.loads(c.policy_checks_json)
                if any(not chk.get("passed", True) for chk in checks.values()):
                    policy_violations_count += 1
            except Exception:
                pass
                
    return {
        "totalApproved": total_approved,
        "pendingCount": pending_count,
        "highRiskCount": high_risk_count,
        "policyViolationsCount": policy_violations_count
    }

@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim_detail(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim.to_dict()

@router.post("/upload", response_model=ClaimResponse)
async def upload_claim(
    submitter: str = Form("Vigneshwar S."),
    department: str = Form("IT Department"),
    merchant: str = Form("Store Purchase"),
    category: str = Form("Lab Equipment"),
    amount: float = Form(1000.0),
    is_tampered: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    claim_id = f"EV-{merchant[:3].upper()}-{str(uuid.uuid4())[:4].upper()}"
    
    # Save original uploaded image file
    filename = f"{claim_id}_orig.jpg"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if file:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    else:
        # Generate placeholder image if no direct file attached
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (400, 500), color=(255, 253, 245))
        d = ImageDraw.Draw(img)
        d.text((20, 20), f"{merchant}\nDate: {datetime.date.today()}\nTotal: ₹{amount}", fill=(0, 0, 0))
        img.save(file_path)

    # 1. Run ELA Forensics Scan
    ela_url, ela_score, detected_tamper = perform_ela_analysis(file_path, claim_id)
    if is_tampered:
        detected_tamper = True
        ela_score = max(ela_score, 0.89)

    # 2. Run OCR Extraction
    ocr_data = parse_receipt_ocr(file_path)
    if file and ocr_data:
        if ocr_data.get("merchant"):
            merchant = ocr_data.get("merchant")
        if ocr_data.get("totalAmount", 0.0) > 0.0:
            amount = float(ocr_data.get("totalAmount"))
        if ocr_data.get("category"):
            category = ocr_data.get("category")

    # 3. Evaluate Corporate Policy Rules
    policy = db.query(Policy).first()
    policy_checks, policy_failed = evaluate_policy_rules(
        amount, category, merchant, submitter, detected_tamper, policy, line_items=ocr_data.get("lineItems", [])
    )

    # 4. Calculate ML Isolation Forest Fraud Score
    anomaly_score, risk_level = calculate_fraud_anomaly_score(amount, category, ela_score, detected_tamper, policy_failed)

    # Create Claim record in DB
    new_claim = Claim(
        id=claim_id,
        submitter=submitter,
        department=department,
        merchant=merchant,
        category=category,
        amount=amount,
        date=ocr_data.get("date", datetime.date.today().isoformat()),
        status="Pending",
        risk_level=risk_level,
        anomaly_score=anomaly_score,
        description=f"Claim processed via API upload for {merchant}.",
        original_image_path=f"/uploads/{filename}",
        ela_image_path=ela_url,
        policy_checks_json=json.dumps(policy_checks),
        ocr_data_json=json.dumps(ocr_data)
    )

    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)
    return new_claim.to_dict()

@router.post("/{claim_id}/approve", response_model=ClaimResponse)
def approve_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    claim.status = "Approved"
    db.commit()
    db.refresh(claim)

    if claim.telegram_chat_id:
        msg = (
            f"🎉 *Expense Claim Approved!*\n\n"
            f"Your expense claim has been accepted and approved by the Finance Admin.\n\n"
            f"• *Claim ID:* `{claim.id}`\n"
            f"• *Merchant:* {claim.merchant}\n"
            f"• *Amount:* ₹{claim.amount:,.2f}\n"
            f"• *Status:* ✅ Approved\n\n"
            f"💰 Reimbursement will be processed shortly."
        )
        send_telegram_message(claim.telegram_chat_id, msg)

    return claim.to_dict()

@router.post("/{claim_id}/reject", response_model=ClaimResponse)
def reject_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    claim.status = "Rejected"
    db.commit()
    db.refresh(claim)

    if claim.telegram_chat_id:
        msg = (
            f"❌ *Expense Claim Rejected*\n\n"
            f"Your expense claim has been reviewed and rejected by the Finance Admin.\n\n"
            f"• *Claim ID:* `{claim.id}`\n"
            f"• *Merchant:* {claim.merchant}\n"
            f"• *Amount:* ₹{claim.amount:,.2f}\n"
            f"• *Status:* ❌ Rejected\n\n"
            f"⚠️ If you believe this is an error or need clarification, please contact your Finance Manager."
        )
        send_telegram_message(claim.telegram_chat_id, msg)

    return claim.to_dict()

