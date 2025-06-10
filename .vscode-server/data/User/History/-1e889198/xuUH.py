import pytest
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from unittest.mock import AsyncMock, MagicMock
import keygenie_bot

@pytest.mark.asyncio
async def test_start_command():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_photo = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await keygenie_bot.start(update, context)
    update.message.reply_photo.assert_called_once()
    args = update.message.reply_photo.call_args[1]
    assert "caption" in args and "👾 Welcome to *KeyGenie* Bot!" in args["caption"]

@pytest.mark.asyncio
async def test_cmds_command():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_markdown = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await keygenie_bot.cmds(update, context)
    update.message.reply_markdown.assert_called_once()
    args = update.message.reply_markdown.call_args[0][0]
    assert "/start" in args and "/buy" in args

@pytest.mark.asyncio
async def test_help_command():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_markdown = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await keygenie_bot.help_command(update, context)
    update.message.reply_markdown.assert_called_once()
    args = update.message.reply_markdown.call_args[0][0]
    assert "🛒 *How to Use KeyGenie Bot:*" in args

@pytest.mark.asyncio
async def test_terms_command():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_markdown = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await keygenie_bot.terms(update, context)
    update.message.reply_markdown.assert_called_once()
    args = update.message.reply_markdown.call_args[0][0]
    assert "Terms and Conditions" in args

@pytest.mark.asyncio
async def test_buy_flow():
    # Test /buy command start
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.job_queue = MagicMock()
    context.job_queue.run_once = MagicMock()  # Changed to MagicMock to avoid async warning
    context.job_queue.get_jobs_by_name = MagicMock(return_value=[])

    state = await keygenie_bot.buy_start(update, context)
    assert state == keygenie_bot.SELECTING_PRODUCT
    update.message.reply_text.assert_called_once()
    args = update.message.reply_text.call_args[1]
    assert isinstance(args['reply_markup'], InlineKeyboardMarkup)
    assert "🛒 Please select a product" in args['text']

    # Test product selection with valid product
    update.callback_query = MagicMock()
    update.callback_query.data = "SELECT_Category 1"  # Use actual product from config
    update.callback_query.from_user = MagicMock()
    update.callback_query.from_user.id = 12345
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    update.callback_query.message = MagicMock()
    update.callback_query.message.reply_text = AsyncMock()
    context.user_data = {}

    state = await keygenie_bot.product_selected(update, context)
    assert state == keygenie_bot.WAITING_FOR_TXID
    update.callback_query.answer.assert_called_once()
    update.callback_query.edit_message_text.assert_called_once()

    # Test cancel button
    update.callback_query.data = "CANCEL"
    state = await keygenie_bot.product_selected(update, context)
    assert state == ConversationHandler.END

    # Test back button - this should show products again
    update.callback_query.data = "BACK_TO_PRODUCTS"
    update.callback_query.edit_message_text.reset_mock()
    state = await keygenie_bot.product_selected(update, context)
    assert state == keygenie_bot.SELECTING_PRODUCT
    update.callback_query.edit_message_text.assert_called_once()

@pytest.mark.asyncio
async def test_timeout():
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.job = MagicMock()
    context.job.data = 12345

    await keygenie_bot.cancel_purchase_flow(context)
    context.bot.send_message.assert_called_once()
    args = context.bot.send_message.call_args[1]
    assert "timed out" in args['text']

@pytest.mark.asyncio
async def test_txid_handling():
    # Test valid TXID submission
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.text = "test_txid_123"
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.username = "testuser"
    
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.user_data = {'selected_product': 'Product A'}

    state = await keygenie_bot.txid_received(update, context)
    assert state == ConversationHandler.END
    assert update.message.reply_text.call_count >= 1

    # Test missing product
    context.user_data = {}
    state = await keygenie_bot.txid_received(update, context)
    assert state == ConversationHandler.END
    update.message.reply_text.assert_called_with(
        "❌ No product selected. Please use /buy to start the purchase flow."
    )

@pytest.mark.asyncio
async def test_error_handling():
    # Test admin notification failure
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.text = "test_txid_123"
    update.message.reply_text = AsyncMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock(side_effect=Exception("Test error"))
    context.user_data = {'selected_product': 'Product A'}

    state = await keygenie_bot.txid_received(update, context)
    assert state == ConversationHandler.END
    # Should see error message to user
    assert any("Failed to notify admin" in call.args[0] 
              for call in update.message.reply_text.call_args_list)

@pytest.mark.asyncio
async def test_random_message_handler():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await keygenie_bot.handle_random_message(update, context)
    update.message.reply_text.assert_called_once()
    args = update.message.reply_text.call_args[0][0]
    assert any(response in args for response in keygenie_bot.HUMOROUS_RESPONSES)
