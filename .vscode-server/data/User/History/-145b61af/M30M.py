import asyncio
import httpx
import json
import os
import logging

import config

USER_DATA_FILE = "user_data.json"
LOG_FILE = "payment_verification_cron.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def verify_payment(txid: str, product: str) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.PAYMENT_VERIFICATION_API_URL,
                headers={"Authorization": f"Bearer {config.PAYMENT_VERIFICATION_API_KEY}"},
                json={"txid": txid, "product": product},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("verified", False)
    except Exception as e:
        logging.error(f"Payment verification API error: {e}")
        return False

async def process_pending_payments():
    user_data = load_user_data()
    updated = False

    for user_id, record in user_data.items():
        purchases = record.get("purchases", [])
        for purchase in purchases:
            if purchase.get("status") == "pending":
                txid = purchase.get("txid")
                product = purchase.get("product")
                if not txid or not product:
                    continue
                verified = await verify_payment(txid, product)
                if verified:
                    purchase["status"] = "verified"
                    logging.info(f"Payment verified for user {user_id}, product {product}, txid {txid}")
                    updated = True
                else:
                    logging.info(f"Payment not verified yet for user {user_id}, product {product}, txid {txid}")

    if updated:
        save_user_data(user_data)

if __name__ == "__main__":
    asyncio.run(process_pending_payments())
