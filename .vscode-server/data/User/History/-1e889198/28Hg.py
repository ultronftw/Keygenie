import pytest
from telegram import Update
from telegram.ext import ContextTypes
from unittest.mock import AsyncMock, MagicMock
import keygenie_bot

@pytest.mark.asyncio
async def test_start_command():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_markdown = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await keygenie_bot.start(update, context)
    update.message.reply_markdown.assert_called_once_with(
        "👾 Welcome to *KeyGenie* Bot!\nYour gateway to secure key purchases.\n\nUse /cmds to see available commands."
    )

@pytest.mark.asyncio
async def test_cmds_command():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await keygenie_bot.cmds(update, context)
    update.message.reply_text.assert_called_once()
    args = update.message.reply_text.call_args[0][0]
    assert "/start" in args and "/buy" in args

@pytest.mark.asyncio
async def test_help_command():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await keygenie_bot.help_command(update, context)
    update.message.reply_text.assert_called_once()
    args = update.message.reply_text.call_args[0][0]
    assert "To purchase a product" in args

@pytest.mark.asyncio
async def test_terms_command():
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await keygenie_bot.terms(update, context)
    update.message.reply_text.assert_called_once()
    args = update.message.reply_text.call_args[0][0]
    assert "Terms and Conditions" in args

# Additional tests for /buy flow, refund requests, validation, and notifications would be added here.
