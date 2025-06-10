import pytest
from telegram import Update
from telegram.ext import ContextTypes
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

# Additional tests for /buy flow, refund requests, validation, and notifications would be added here.
