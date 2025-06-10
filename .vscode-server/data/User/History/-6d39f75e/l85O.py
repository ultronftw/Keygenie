# Configuration file for KeyGenie bot

BOT_TOKEN = "7451215429:AAHGUMU5Vq8FYlfPymIopxhLPu8AowwVdKE"
ADMIN_ID = 123456789  # Replace with your Telegram user ID (int)

BTC_ADDRESS = "your_btc_address"
LTC_ADDRESS = "your_ltc_address"
USDT_ADDRESS = "your_usdt_address"

PRODUCTS = {
    "Category 1": {"price": "20$", "key": "KEY_FOR_CATEGORY_1"},
    "Category 2": {"price": "30$", "key": "KEY_FOR_CATEGORY_2"},
    "Category 3": {"price": "20$", "key": "KEY_FOR_CATEGORY_3"},
    "Category 4": {"price": "50$", "key": "KEY_FOR_CATEGORY_4"},
}

# Auto verification toggle: True to enable automatic payment verification, False for manual only
AUTO_VERIFICATION_ENABLED = False

# Payment verification API endpoint and API key (example placeholders)
PAYMENT_VERIFICATION_API_URL = "https://api.example.com/verify_payment"
PAYMENT_VERIFICATION_API_KEY = "your_api_key_here"
