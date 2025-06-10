import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
import config

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for ConversationHandler
SELECTING_PRODUCT, WAITING_FOR_TXID = range(2)

# Load configuration from config.py
BOT_TOKEN = config.BOT_TOKEN
ADMIN_ID = config.ADMIN_ID
BTC_ADDRESS = config.BTC_ADDRESS
LTC_ADDRESS = config.LTC_ADDRESS
USDT_ADDRESS = config.USDT_ADDRESS
PRODUCTS = config.PRODUCTS

# Command handlers

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot.")
    welcome_message = (
        "👾 Welcome to *KeyGenie* Bot!\n"
        "Your gateway to secure key purchases.\n\n"
        "Use /cmds to see available commands."
    )
    await update.message.reply_markdown(welcome_message)

async def cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_text = (
        "📜 *Available Commands:*\n"
        "/start — Welcome message\n"
        "/cmds — List commands\n"
        "/buy — Start purchase flow\n"
        "/info — User info (optional)\n"
        "/help — How to use the bot\n"
        "/terms — Terms and conditions\n"
        "/status — Check payment status\n"
        "/contact — Contact admin"
    )
    await update.message.reply_markdown(commands_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛒 *How to Use KeyGenie Bot:*\n"
        "1. Use /buy to start the purchase flow.\n"
        "2. Select a product from the catalog.\n"
        "3. View the price and payment addresses.\n"
        "4. Send your payment and then submit the transaction ID (TXID).\n"
        "5. An admin will verify your payment and send you the key.\n\n"
        "Other commands:\n"
        "/start - Welcome message\n"
        "/cmds - List commands\n"
        "/info - Show your user info\n"
        "/help - Show this help message\n"
        "/terms - Show terms and conditions\n"
        "/status - Check payment status\n"
        "/contact - Contact admin\n"
        "/cancel - Cancel current operation"
    )
    await update.message.reply_markdown(help_text)

async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    terms_text = (
        "📜 *Terms and Conditions:*\n"
        "1. All sales are final.\n"
        "2. Payment verification is manual.\n"
        "3. Please ensure you send the correct amount.\n"
        "4. Contact admin for any issues."
    )
    await update.message.reply_markdown(terms_text)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    info_text = (
        f"👤 *User Info:*\n"
        f"Username: @{user.username if user.username else 'N/A'}\n"
        f"User ID: {user.id}\n"
        f"First Name: {user.first_name}\n"
        f"Last Name: {user.last_name if user.last_name else 'N/A'}"
    )
    await update.message.reply_markdown(info_text)

# Purchase flow handlers

async def buy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=name)] for name in PRODUCTS.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🛒 Please select a product to buy:", reply_markup=reply_markup
    )
    return SELECTING_PRODUCT

async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product = query.data
    if product not in PRODUCTS:
        await query.edit_message_text(
            "❌ Invalid product selected. Please use /buy to start again."
        )
        return ConversationHandler.END

    context.user_data['selected_product'] = product
    price = PRODUCTS[product]['price']
    payment_info = (
        f"💰 Price for {product}: {price}\n\n"
        f"Please send payment to one of the following addresses:\n"
        f"BTC: {BTC_ADDRESS}\n"
        f"LTC: {LTC_ADDRESS}\n"
        f"USDT: {USDT_ADDRESS}\n\n"
        "After payment, please send the transaction ID (TXID) here."
    )
    await query.edit_message_text(payment_info)
    await query.message.reply_text("⚠️ Please make sure to double-check your payment details before sending the TXID.")
    return WAITING_FOR_TXID

import httpx
import json
import os

USER_DATA_FILE = "user_data.json"

def load_user_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def deliver_key(user_id: int, product: str, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_user_data()
    user_record = user_data.get(str(user_id), {"purchases": []})
    product_key = config.PRODUCTS[product]["key"]

    # Send the product key to the user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎉 Your purchase of *{product}* is confirmed!\nHere is your product key:\n`{product_key}`",
            parse_mode="Markdown",
        )
        logger.info(f"Delivered key for {product} to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to deliver key to user {user_id}: {e}")
        return False

    # Update user purchase history
    user_record["purchases"].append({"product": product, "key": product_key})
    user_data[str(user_id)] = user_record
    save_user_data(user_data)
    return True

async def txid_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txid = update.message.text.strip()
    product = context.user_data.get('selected_product')

    if not product:
        await update.message.reply_text(
            "❌ No product selected. Please use /buy to start the purchase flow."
        )
        return ConversationHandler.END

    user = update.effective_user

    if config.AUTO_VERIFICATION_ENABLED:
        verified = await verify_payment(txid, product)
        if verified:
            delivered = await deliver_key(user.id, product, context)
            if delivered:
                await update.message.reply_text(
                    f"✅ Payment verified automatically! Your key for {product} has been sent."
                )
            else:
                await update.message.reply_text(
                    "⚠️ Payment verified but failed to deliver the product key. Please contact admin."
                )
            logger.info(f"Auto verified payment for user {user.id}, product {product}, txid {txid}")
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                "⚠️ Payment could not be verified automatically. It will be reviewed manually."
            )

    # Manual verification fallback
    admin_message = (
        f"📢 Payment TXID received from user @{user.username if user.username else user.id}:\n"
        f"Product: {product}\n"
        f"TXID: {txid}\n\n"
        "Please verify the payment and send the key to the user."
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
        logger.info(f"Notified admin {ADMIN_ID} of payment TXID from user {user.id}")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

    await update.message.reply_text(
        "✅ Thank you! Your payment TXID has been received and is pending verification by the admin."
    )
    await update.message.reply_text("ℹ️ If you have any questions, use /help or contact the admin.")
    return ConversationHandler.END

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Placeholder for payment status checking logic
    await update.message.reply_text(
        "🔍 Payment status feature is coming soon. Please check back later."
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_info = (
        "📞 *Contact Admin:*\n"
        "For support or inquiries, please contact @YourAdminUsername."
    )
    await update.message.reply_markdown(contact_info)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Purchase flow cancelled.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    from telegram.ext import CallbackQueryHandler

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('buy', buy_start)],
        states={
            SELECTING_PRODUCT: [CallbackQueryHandler(product_selected)],
            WAITING_FOR_TXID: [MessageHandler(filters.TEXT & ~filters.COMMAND, txid_received)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('cmds', cmds))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('terms', terms))
    application.add_handler(CommandHandler('info', info))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('contact', contact))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
