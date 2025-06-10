# Configuration file for KeyGenie bot

BOT_TOKEN = "7451215429:AAHGUMU5Vq8FYlfPymIopxhLPu8AowwVdKE"
ADMIN_ID = 123456789  # Replace with your Telegram user ID (int)

BTC_ADDRESS = "your_btc_address"
LTC_ADDRESS = "your_ltc_address"
USDT_ADDRESS = "your_usdt_address"

PRODUCTS = {
    "Product A": {"price": "0.001 BTC", "key": "KEY_FOR_PRODUCT_A"},
    "Product B": {"price": "0.01 LTC", "key": "KEY_FOR_PRODUCT_B"},
    "Product C": {"price": "10 USDT", "key": "KEY_FOR_PRODUCT_C"},
}

# Auto verification toggle: True to enable automatic payment verification, False for manual only
AUTO_VERIFICATION_ENABLED = False

# Payment verification API endpoint and API key (example placeholders)
PAYMENT_VERIFICATION_API_URL = "https://api.example.com/verify_payment"
PAYMENT_VERIFICATION_API_KEY = "your_api_key_here"
