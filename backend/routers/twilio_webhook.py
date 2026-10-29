import os
import uuid
import datetime
import json
import httpx
from fastapi import APIRouter, Form, Response, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Claim, Policy
from backend.config import UPLOAD_DIR, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
from backend.services.ela_service import perform_ela_analysis
from backend.services.ocr_service import parse_receipt_ocr
from backend.services.fraud_service import calculate_fraud_anomaly_score
from backend.services.policy_service import evaluate_policy_rules

router = APIRouter(prefix="/api/webhook", tags=["Twilio WhatsApp Webhook"])

@router.post("/whatsapp")
async def twilio_whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(None),
    MediaUrl0: str = Form(None),
    NumMedia: int = Form(0),
    db: Session = Depends(get_db)
):
    """
    Twilio WhatsApp Webhook Endpoint.
    Handles incoming messages from live Twilio WhatsApp Sandbox / Business Account.
    Downloads bill image, executes OCR + ELA + Fraud Analysis, inserts to Database,
    and returns TwiML XML response.
    """
    phone_clean = From.replace("whatsapp:", "")
    submitter_name = f"Employee ({phone_clean})"
    
    if MediaUrl0:
        claim_id = f"EV-WA-{str(uuid.uuid4())[:4].upper()}"
        filename = f"{claim_id}_orig.jpg"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Download media file from Twilio CDN (using HTTP basic auth if credentials provided)
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None
        try:
            async with httpx.AsyncClient(auth=auth) as client:
                res = await client.get(MediaUrl0, follow_redirects=True)
                if res.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(res.content)
        except Exception as e:
            print(f"Failed to download media from Twilio URL {MediaUrl0}: {e}")

        # Parse merchant and amount from text body or use extracted values
        merchant = "Store / Vendor"
        category = "Food & Beverage"
        amount = 1500.0

        if Body:
            cleaned_text = Body.replace("₹", "").replace("INR", "").replace("Rs", "").strip()
            words = cleaned_text.split()
            for word in words:
                try:
                    val = float(word)
                    if val > 0:
                        amount = val
                        break
                except ValueError:
                    pass

        # 1. Run ELA Forensics
        ela_url, ela_score, is_tampered = perform_ela_analysis(file_path, claim_id)

        # 2. Run OCR Extraction
        ocr_data = parse_receipt_ocr(file_path, hint_merchant=merchant, hint_amount=amount)
        if ocr_data.get("merchant"):
            merchant = ocr_data["merchant"]

        # 3. Evaluate Policy Rules
        policy = db.query(Policy).first()
        policy_checks, policy_failed = evaluate_policy_rules(amount, category, merchant, submitter_name, is_tampered, policy)

        # 4. Calculate ML Fraud Score
        anomaly_score, risk_level = calculate_fraud_anomaly_score(amount, category, ela_score, is_tampered, policy_failed)

        # Create Claim in Database
        new_claim = Claim(
            id=claim_id,
            submitter=submitter_name,
            department="Operations",
            merchant=merchant,
            category=category,
            amount=amount,
            date=datetime.date.today().isoformat(),
            status="Pending",
            risk_level=risk_level,
            anomaly_score=anomaly_score,
            description=f"Direct WhatsApp submission from phone {phone_clean}.",
            original_image_path=f"/uploads/{filename}",
            ela_image_path=ela_url,
            policy_checks_json=json.dumps(policy_checks),
            ocr_data_json=json.dumps(ocr_data)
        )

        db.add(new_claim)
        db.commit()

        # Build TwiML XML response
        if risk_level == "High":
            reply_text = f"⚠️ *Audit Warning Flagged!*\n\n• *Claim ID:* {claim_id}\n• *Amount:* ₹{amount:,.2f}\n• *Status:* Flagged for Audit\n\n🔴 Digital text modifications or policy breaches detected. Submitted to admin dashboard for review."
        else:
            reply_text = f"✅ *Receipt received and parsed successfully!*\n\n• *Claim ID:* {claim_id}\n• *Merchant:* {merchant}\n• *Amount:* ₹{amount:,.2f}\n\n🟢 Submitted to Finance Dashboard for manager approval."

        xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_text}</Message>
</Response>"""
        return Response(content=xml_response, media_type="application/xml")

    else:
        xml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Please send a photo of your receipt or bill to submit an expense claim.</Message>
</Response>"""
        return Response(content=xml_response, media_type="application/xml")

