"""
Telegram Bot Integration for Expense Vision
Uses Telegram Bot API (Long Polling via httpx) to receive receipt photos,
run ELA Forensics + OCR + Policy/Fraud Engine, and store claim in database.
"""
import os
import sys
import time
import uuid
import datetime
import json
import httpx

# Add root project dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.database import SessionLocal
from backend.models import Claim, Policy
from backend.config import UPLOAD_DIR
from backend.services.ela_service import perform_ela_analysis
from backend.services.ocr_service import parse_receipt_ocr
from backend.services.fraud_service import calculate_fraud_anomaly_score
from backend.services.policy_service import evaluate_policy_rules

TOKEN_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "telegram_token.txt")

def get_bot_token():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if token:
        return token
        
    if os.path.exists(TOKEN_FILE_PATH):
        with open(TOKEN_FILE_PATH, "r", encoding="utf-8") as f:
            token = f.read().strip()
            if token:
                return token
                
    # If not found in env or file, prompt interactively
    print("=======================================================================")
    print("🔑 TELEGRAM BOT TOKEN REQUIRED")
    print("Get your token from @BotFather on Telegram (e.g. 7123456789:AAFxxx...)")
    print("=======================================================================")
    try:
        token = input("Paste your Telegram Bot Token here: ").strip()
        if token:
            with open(TOKEN_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(token)
            print(f"✅ Token saved to {TOKEN_FILE_PATH}!")
            return token
    except Exception as e:
        print(f"Error reading input: {e}")
    return ""

def start_bot():
    token = get_bot_token()
    if not token:
        print("❌ Error: Telegram Bot Token is missing. Bot cannot start.")
        return

    api_url = f"https://api.telegram.org/bot{token}"
    print("=======================================================================")
    print("🤖 Starting Expense Vision Telegram Bot...")
    print("Send receipt photos to your Telegram bot!")
    print("=======================================================================")
    offset = 0

    with httpx.Client(timeout=30.0) as client:
        while True:
            try:
                response = client.get(f"{api_url}/getUpdates", params={"offset": offset, "timeout": 20})
                if response.status_code != 200:
                    time.sleep(3)
                    continue

                updates = response.json().get("result", [])
                for update in updates:
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    chat_id = message.get("chat", {}).get("id")
                    user_name = message.get("from", {}).get("first_name", "Employee")
                    
                    if not chat_id:
                        continue

                    # Handle text messages without photo
                    if "photo" not in message:
                        welcome = (
                            f"👋 Hello {user_name}!\n\n"
                            "Welcome to *Expense Vision Bot*.\n"
                            "📸 *Please send me a photo of your receipt/bill* to file an expense claim."
                        )
                        client.post(f"{api_url}/sendMessage", json={
                            "chat_id": chat_id,
                            "text": welcome,
                            "parse_mode": "Markdown"
                        })
                        continue

                    # Handle photo attachment
                    photos = message.get("photo", [])
                    if photos:
                        client.post(f"{api_url}/sendMessage", json={
                            "chat_id": chat_id,
                            "text": "🔎 *Processing receipt...* Running OCR, ELA Forensics & Isolation Forest Anomaly Detection.",
                            "parse_mode": "Markdown"
                        })
                        
                        # Get largest photo size
                        file_id = photos[-1]["file_id"]
                        file_info = client.get(f"{api_url}/getFile", params={"file_id": file_id}).json()
                        file_path_tg = file_info["result"]["file_path"]
                        download_url = f"https://api.telegram.org/file/bot{token}/{file_path_tg}"

                        # Save photo locally
                        claim_id = f"EV-TG-{str(uuid.uuid4())[:4].upper()}"
                        filename = f"{claim_id}_orig.jpg"
                        file_path = os.path.join(UPLOAD_DIR, filename)

                        img_res = client.get(download_url)
                        with open(file_path, "wb") as f:
                            f.write(img_res.content)

                        # Process Claim
                        db = SessionLocal()
                        try:
                            # 1. ELA Analysis
                            ela_url, ela_score, is_tampered = perform_ela_analysis(file_path, claim_id)
                            # 2. OCR Extraction
                            ocr_data = parse_receipt_ocr(file_path)
                            merchant = ocr_data.get("merchant", "Store / Vendor")
                            amount = float(ocr_data.get("totalAmount", 0.0))
                            category = ocr_data.get("category", "Operations")

                            # 3. Policy Check & Anomaly Score
                            policy = db.query(Policy).first()
                            submitter = f"{user_name} (Telegram)"
                            policy_checks, policy_failed = evaluate_policy_rules(
                                amount, category, merchant, submitter, is_tampered, policy, line_items=ocr_data.get("lineItems", [])
                            )
                            anomaly_score, risk_level = calculate_fraud_anomaly_score(amount, category, ela_score, is_tampered, policy_failed)

                            new_claim = Claim(
                                id=claim_id,
                                submitter=submitter,
                                department="Operations",
                                merchant=merchant,
                                category=category,
                                amount=amount,
                                date=ocr_data.get("date", datetime.date.today().isoformat()),
                                status="Pending",
                                risk_level=risk_level,
                                anomaly_score=anomaly_score,
                                description=f"Submitted via Telegram Bot by {user_name}.",
                                telegram_chat_id=str(chat_id),
                                original_image_path=f"/uploads/{filename}",
                                ela_image_path=ela_url,
                                policy_checks_json=json.dumps(policy_checks),
                                ocr_data_json=json.dumps(ocr_data)
                            )
                            db.add(new_claim)
                            db.commit()

                            if risk_level == "High":
                                reply = (
                                    f"⚠️ *Receipt Uploaded Successfully (Flagged for Review)*\n\n"
                                    f"• *Claim ID:* `{claim_id}`\n"
                                    f"• *Merchant:* {merchant}\n"
                                    f"• *Amount:* ₹{amount:,.2f}\n"
                                    f"• *Risk Assessment:* High Risk (Score: {anomaly_score * 100:.1f}%)\n\n"
                                    f"📋 Your bill has been submitted to the Finance Admin for manual verification. Our audit team will review the claim and reach out to you shortly."
                                )
                            elif risk_level == "Medium":
                                reply = (
                                    f"✅ *Receipt Uploaded Successfully!*\n\n"
                                    f"• *Claim ID:* `{claim_id}`\n"
                                    f"• *Merchant:* {merchant}\n"
                                    f"• *Amount:* ₹{amount:,.2f}\n"
                                    f"• *Category:* {category}\n"
                                    f"• *Risk Assessment:* Medium Risk (Score: {anomaly_score * 100:.1f}%)\n\n"
                                    f"📩 Your bill has been successfully submitted to your Finance Admin. They will review your claim shortly."
                                )
                            else:
                                reply = (
                                    f"✅ *Receipt Uploaded Successfully!*\n\n"
                                    f"• *Claim ID:* `{claim_id}`\n"
                                    f"• *Merchant:* {merchant}\n"
                                    f"• *Amount:* ₹{amount:,.2f}\n"
                                    f"• *Category:* {category}\n"
                                    f"• *Risk Assessment:* Low Risk (Score: {anomaly_score * 100:.1f}%)\n\n"
                                    f"📩 Your bill has been successfully submitted to your Finance Admin. You will receive an instant notification here once it is approved or rejected."
                                )

                            client.post(f"{api_url}/sendMessage", json={
                                "chat_id": chat_id,
                                "text": reply,
                                "parse_mode": "Markdown"
                            })
                            print(f"✅ Processed claim {claim_id} for {merchant} (₹{amount:,.2f}) -> {risk_level} Risk")
                        finally:
                            db.close()
            except Exception as e:
                print(f"Error in bot loop: {e}")
                time.sleep(3)

if __name__ == "__main__":
    start_bot()

