#!/usr/bin/env python
"""
PWN Ascension Engine — Replit Webhook Version
Entry point for the entire Telegram bot.
"""

import os
import logging
from flask import Flask, request

from telegram import Bot, Update

# ROUTER
from router import handle_update

# Logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Telegram Bot token (NEVER hardcode)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise Exception("TELEGRAM_TOKEN environment variable not set!")

bot = Bot(token=TELEGRAM_TOKEN)

# Flask app
app = Flask(__name__)


@app.route("/")
def home():
    """Landing page — required for uptime pings."""
    return "PWN Ascension Engine is running."


@app.route("/webhook", methods=["POST"])
def webhook():
    """Main webhook entry point."""
    try:
        json_update = request.get_json(force=True)
        update = Update.de_json(json_update, bot)

        logger.info(f"Incoming update: {json_update}")

        # Forward to unified router
        handle_update(bot, update)

    except Exception as e:
        logger.error(f"Webhook error: {e}")

    return "ok"


if __name__ == "__main__":
    # Replit requires host=0.0.0.0
    app.run(host="0.0.0.0", port=8080)
