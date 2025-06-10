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

# Timer job names
TIMEOUT_JOB_NAME = "purchase_timeout_{}"

# Load configuration from config.py
BOT_TOKEN = config.BOT_TOKEN
ADMIN_ID = config.ADMIN_ID
BTC_ADDRESS = config.BTC_ADDRESS
LTC_ADDRESS = config.LTC_ADDRESS
USDT_ADDRESS = config.USDT_ADDRESS
PRODUCTS = config.PRODUCTS

def clear_purchase_timeout(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Clear the purchase timeout job for a user"""
    if context.job_queue is None:
        return
    current_jobs = context.job_queue.get_jobs_by_name(TIMEOUT_JOB_NAME.format(user_id))
    for job in current_jobs:
        job.schedule_removal()

async def verify_payment(txid: str, product: str) -> bool:
    # Placeholder for automatic payment verification logic
    # Currently, automatic verification is disabled; always return False
    return False

# Command handlers

# Preset humorous responses for random messages
HUMOROUS_RESPONSES = [
    "😄 I'm just a bot, but I love a good joke! Try /cmds to see what I can do.",
    "🤖 Beep boop! I don't understand that, but I'm here to help with /buy and more.",
    "😂 That sounds funny! But let's stick to keys and payments. Use /cmds for commands.",
    "😜 I'm not great at chit-chat, but I can help you buy keys! Try /buy.",
    "😎 Cool story! Now, how about some keys? Use /cmds to get started.",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"User {update.effective_user.id} started the bot.")
    welcome_message = (
        "👾 Welcome to *KeyGenie* Bot!\n"
        "Your gateway to secure key purchases.\n\n"
        "Use /cmds to see available commands."
    )
    # Send image with welcome message to grab attention
    image_path = "robot_head.jpg"
    await update.message.reply_photo(photo=open(image_path, "rb"), caption=welcome_message)
    # No need to delete image later, only show on /start

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

async def handle_random_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random
    response = random.choice(HUMOROUS_RESPONSES)
    await update.message.reply_text(response)

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

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    """Show product selection keyboard"""
    product_names = list(PRODUCTS.keys())
    keyboard = []
    row = []
    for i, name in enumerate(product_names):
        row.append(InlineKeyboardButton(name, callback_data=f"SELECT_{name}"))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    # Add control buttons
    keyboard.append([
        InlineKeyboardButton("❌ Cancel", callback_data="CANCEL"),
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🛒 Please select a product to buy:"
    
    if edit and update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup)

async def buy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the purchase flow"""
    logger.info(f"User {update.effective_user.id} started /buy command.")
    
    # Clear any existing timeout jobs for this user
    clear_purchase_timeout(context, update.effective_user.id)
    
    # Start new 30-minute timer if job queue is available
    if context.job_queue is not None:
        context.job_queue.run_once(
            cancel_purchase_flow, 
            1800, 
            data=update.effective_user.id,
            name=TIMEOUT_JOB_NAME.format(update.effective_user.id)
        )
    
    await show_products(update, context)
    return SELECTING_PRODUCT

async def cancel_purchase_flow(context: ContextTypes.DEFAULT_TYPE):
    """Handle purchase flow timeout"""
    user_id = context.job.data
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="⏰ Purchase flow timed out after 30 minutes. Please start again with /buy if you wish."
        )
    except Exception as e:
        logger.error(f"Failed to send timeout message to user {user_id}: {e}")

async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product selection"""
    query = update.callback_query
    await query.answer()
    
    if not query.data:
        await query.edit_message_text("❌ Invalid selection. Please try again.")
        return ConversationHandler.END
        
    action = query.data.split('_')[0] if '_' in query.data else query.data
    
    if action == "CANCEL":
        await query.edit_message_text("❌ Purchase cancelled. Use /buy to start again.")
        clear_purchase_timeout(context, query.from_user.id)
        return ConversationHandler.END
    
    if query.data == "BACK_TO_PRODUCTS":
        await show_products(update, context, edit=True)
        return SELECTING_PRODUCT
        
    if action != "SELECT":
        await query.edit_message_text("❌ Invalid selection. Please use /buy to start again.")
        return ConversationHandler.END
        
    product = query.data.split('_', 1)[1]
    if product not in PRODUCTS:
        await query.edit_message_text("❌ Invalid product selected. Please use /buy to start again.")
        return ConversationHandler.END

    logger.info(f"User {query.from_user.id} selected product: {product}")
    context.user_data['selected_product'] = product
    price = PRODUCTS[product]['price']
    
    # Create keyboard with payment options and back button
    keyboard = [
        [InlineKeyboardButton("⬅️ Back", callback_data="BACK_TO_PRODUCTS")],
        [InlineKeyboardButton("❌ Cancel", callback_data="CANCEL")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    payment_info = (
        f"💰 Price for {product}: {price}\n\n"
        f"Please send payment to one of the following addresses:\n"
        f"BTC: `{BTC_ADDRESS}`\n"
        f"LTC: `{LTC_ADDRESS}`\n"
        f"USDT: `{USDT_ADDRESS}`\n\n"
        "After payment, please send the transaction ID (TXID) here."
    )
    
    try:
        await query.edit_message_text(
            text=payment_info,
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        # If MarkdownV2 fails, try without formatting
        await query.edit_message_text(
            text=payment_info.replace('`', ''),
            reply_markup=reply_markup
        )
    
    await query.message.reply_text(
        "⚠️ Please make sure to double-check your payment details before sending the TXID.\n"
        "You have 30 minutes to complete the purchase."
    )
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
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="MarkdownV2")
        logger.info(f"Notified admin {ADMIN_ID} of payment TXID from user {user.id}")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")
        await update.message.reply_text(
            "⚠️ Failed to notify admin. Please contact support or try again later."
        )
        return ConversationHandler.END

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
    logger.info("Starting bot...")

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('buy', buy_start)],
        states={
            SELECTING_PRODUCT: [
                CallbackQueryHandler(product_selected),
                CommandHandler('cancel', cancel)
            ],
            WAITING_FOR_TXID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, txid_received),
                CallbackQueryHandler(product_selected),  # Handle back/cancel buttons
                CommandHandler('cancel', cancel)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )

    # Add handlers in specific order
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('cmds', cmds))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('terms', terms))
    application.add_handler(CommandHandler('info', info))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('contact', contact))
    application.add_handler(conv_handler)

    # Add handler for random messages to reply with humor
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_random_message))

    logger.info("Bot handlers registered, starting polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
