
import os
import re
import requests
from bs4 import BeautifulSoup
from decimal import Decimal


def get_amount():
    url = os.environ["TARGET_URL"]
    selector = os.environ["CSS_SELECTOR"]

    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; PersonalMonitor/1.0)"
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    element = soup.select_one(selector)

    if element is None:
        raise ValueError(f"Element not found: {selector}")

    text = element.get_text(strip=True)

    # Extract numeric value
    cleaned = re.sub(r"[^\d.,\-]", "", text)

    # Example: 12,458.72 -> 12458.72
    cleaned = cleaned.replace(",", "")

    amount = Decimal(cleaned)

    if amount < 0:
        raise ValueError("Amount cannot be negative")

    return text, amount


def send_telegram_message(message):
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": message
        },
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError("Telegram API returned an error")


def main():
    text, amount = get_amount()

    message = (
        "📊 Website Monitor\n\n"
        f"💰 Current amount: {text}\n"
        f"🔢 Parsed value: {amount}"
    )

    print(message)

    send_telegram_message(message)


if __name__ == "__main__":
    main()
