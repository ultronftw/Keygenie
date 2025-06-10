# KeyGenie Bot

KeyGenie Bot is a Telegram bot that facilitates secure key purchases using cryptocurrency payments. It provides a user-friendly interface for selecting products, submitting payment proofs, and receiving product keys upon payment verification. Admins can manually approve payments and deliver keys to users.

## Features

- Browse and select products with prices in USDT.
- Submit payment proof via transaction ID or screenshot.
- Admin approval workflow for payment verification.
- Payment verification cron job to automate status updates.
- User-friendly commands and help messages.
- Contact admin for support.

## Installation

### Prerequisites

- Python 3.8 or higher
- Telegram bot token (create a bot via BotFather)
- Cryptocurrency wallet addresses for BTC, LTC, and USDT
- Payment verification API (optional, for automatic verification)

### Setup

1. Clone or download the repository.

2. Create and activate a Python virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure the bot by editing `config.py`:

- Set your Telegram bot token in `BOT_TOKEN`.
- Set the admin Telegram user ID in `ADMIN_ID`.
- Set the admin Telegram username in `ADMIN_USERNAME`.
- Set your cryptocurrency wallet addresses (`BTC_ADDRESS`, `LTC_ADDRESS`, `USDT_ADDRESS`).
- Define your product catalog with prices and keys in `PRODUCTS`.
- (Optional) Configure payment verification API URL and key if using automatic verification.

### Running the Bot

Run the bot with:

```bash
python keygenie_bot.py
```

The bot will start polling Telegram for messages.

### Running the Payment Verification Cron Job

To verify pending payments automatically, run the cron job script:

```bash
python payment_verification_cron.py
```

You can schedule this script to run periodically using cron or a task scheduler.

## Usage

### User Commands

- `/start` - Welcome message and introduction.
- `/cmds` - List available commands.
- `/buy` - Start the purchase flow.
- `/help` - How to use the bot.
- `/terms` - Terms and conditions.
- `/status` - Check payment status.
- `/contact` - Contact admin for support.
- `/cancel` - Cancel current operation.

### Admin Commands

- `/approve <user_id>` - Approve a user's payment and send the product key.

## Important Notes

- Payment verification is manual by default. Automatic verification can be enabled via the config.
- User purchase data and logs are stored in `user_data.json` and `payment_verification_cron.log`.
- Keep your bot token and admin ID confidential.

## Contact

For support or inquiries, contact the admin: [@darkerrrrrrrrrrrrr](https://t.me/darkerrrrrrrrrrrrr)

---

Thank you for using KeyGenie Bot!
