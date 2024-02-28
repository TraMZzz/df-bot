import re
import json
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
import logging
import os

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        if text == "/hello":
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="Hello! How can I help you?"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="I don't understand."
            )
    except Exception as exc:
        logger.error(f"Error in hello_command: {exc}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        if re.search(r"(?i).*hello.*", text):
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="Hello there! Glad you messaged."
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="I don't understand."
            )

    except Exception as exc:
        logger.error(f"Error in hello_message: {exc}")


def lambda_handler(event, context):
    try:
        application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        logger.info(f"event: {json.dumps(event)}")
        asyncio.get_event_loop().run_until_complete(main(event, application))
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")


async def main(event, application):
    try:
        all_commands_handler = MessageHandler(filters.COMMAND, handle_command)
        application.add_handler(all_commands_handler)

        all_messages_handler = MessageHandler(
            filters.TEXT & (~filters.COMMAND), handle_message
        )
        application.add_handler(all_messages_handler)

        for record in event["Records"]:
            body = record["body"]
            if not body:
                logger.warning("Empty body")
                continue
            await application.initialize()
            await application.process_update(
                Update.de_json(json.loads(body), application.bot)
            )
    except Exception as e:
        logger.error(f"Error in main function: {e}")
