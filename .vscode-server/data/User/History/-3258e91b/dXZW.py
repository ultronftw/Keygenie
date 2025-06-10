# Configuration file for KeyGenie bot

BOT_TOKEN = "7451215429:AAHGUMU5Vq8FYlfPymIopxhLPu8AowwVdKE"
ADMIN_ID = 7269446938  # Admin: @darkerrrrrrrrrrrrr (darkerrrrrrrrrrrrr)

# Cryptocurrency wallet addresses for payments
BTC_ADDRESS = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
LTC_ADDRESS = "ltc1qsgdcckjh5s00v2fylsx0vcrxnhnd40zd4xmjez"
USDT_ADDRESS = "0x742d35Cc6634C0532925a3b8D4C9db96590b5c8e"

# Product catalog with prices and keys
PRODUCTS = {
    "Premium Method Pack": {"price": "50 USDT", "key": "PREMIUM-2024-KEYGENIE-001"},
    "Starter Guide": {"price": "20 USDT", "key": "STARTER-2024-KEYGENIE-002"},
    "Advanced Techniques": {"price": "75 USDT", "key": "ADVANCED-2024-KEYGENIE-003"},
    "Complete Bundle": {"price": "120 USDT", "key": "BUNDLE-2024-KEYGENIE-004"},
    "VIP Access": {"price": "200 USDT", "key": "VIP-2024-KEYGENIE-005"},
}

# Auto verification toggle: True to enable automatic payment verification, False for manual only
AUTO_VERIFICATION_ENABLED = False

# Payment verification API endpoint and API key (example placeholders)
PAYMENT_VERIFICATION_API_URL = "https://api.example.com/verify_payment"
PAYMENT_VERIFICATION_API_KEY = "your_api_key_here"

# Bot settings
BOT_NAME = "KeyGenie"
BOT_DESCRIPTION = "Your gateway to secure key purchases"
ADMIN_USERNAME = "@darkerrrrrrrrrrrrr"
