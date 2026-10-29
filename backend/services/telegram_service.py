import os
import httpx

TOKEN_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "telegram_token.txt")

def get_bot_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if token:
        return token
    if os.path.exists(TOKEN_FILE_PATH):
        with open(TOKEN_FILE_PATH, "r", encoding="utf-8") as f:
            token = f.read().strip()
            if token:
                return token
    return ""

def send_telegram_message(chat_id: str, text: str) -> bool:
    """Sends a markdown-formatted message to a specific Telegram chat/user."""
    token = get_bot_token()
    if not token or not chat_id:
        print(f"[TelegramService] Warning: Bot token or chat_id missing (chat_id={chat_id})")
        return False
    try:
        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(api_url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            })
            if resp.status_code == 200:
                print(f"[TelegramService] [SUCCESS] Notification successfully sent to user {chat_id}")
                return True
            else:
                print(f"[TelegramService] [ERROR] Telegram API returned status {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        print(f"[TelegramService] [ERROR] Failed to send Telegram notification to {chat_id}: {e}")
        return False

