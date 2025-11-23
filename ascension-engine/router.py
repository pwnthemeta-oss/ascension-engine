"""
router.py
Unified router for ALL Telegram updates (messages + callbacks).
Replit-safe synchronous version.
"""

import logging
from telegram import Update
from telegram.error import TelegramError

# Database
from database import init_user, get_user

# UI / Screens
from modules.menu import handle_menu_command, handle_menu_callback
from modules.profile import handle_profile_command, handle_profile_callback
from modules.grinding import handle_grind_callback
from modules.badges import handle_badges_callback
from modules.leaderboard import handle_leaderboard_callback
from modules.onboarding import handle_onboarding_callback
from modules.settings import handle_settings_callback
from modules.activity import handle_activity_callback
from modules.challenges import handle_challenges_callback
from modules.help_center import handle_help_command, handle_help_callback

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# MAIN ENTRY POINT FOR ALL TELEGRAM UPDATES
# ------------------------------------------------------------
def handle_update(bot, update: Update):
    """
    Main update entry point for ALL Telegram traffic.

    Handles:
    - /start
    - /menu
    - /profile
    - /help
    - All callback buttons
    - Any unknown message
    """

    try:
        # If no message/callback → ignore
        if not update:
            return

        # -----------------------------------------
        # HANDLE CALLBACK QUERIES (BUTTON CLICK)
        # -----------------------------------------
        if update.callback_query:
            data = update.callback_query.data
            user_id = update.callback_query.from_user.id

            init_user(user_id)

            # ----- MENU ROUTES -----
            if data.startswith("menu"):
                return handle_menu_callback(bot, update)

            # ----- PROFILE ROUTES -----
            if data.startswith("prof"):
                return handle_profile_callback(bot, update)

            # ----- GRIND BUTTON -----
            if data.startswith("grind"):
                return handle_grind_callback(bot, update)

            # ----- BADGES -----
            if data.startswith("badge"):
                return handle_badges_callback(bot, update)

            # ----- LEADERBOARD -----
            if data.startswith("lb_"):
                return handle_leaderboard_callback(bot, update)

            # ----- ONBOARDING -----
            if data.startswith("onb_"):
                return handle_onboarding_callback(bot, update)

            # ----- SETTINGS -----
            if data.startswith("set_"):
                return handle_settings_callback(bot, update)

            # ----- ACTIVITY LOG -----
            if data.startswith("act_"):
                return handle_activity_callback(bot, update)

            # ----- CHALLENGES -----
            if data.startswith("ch_"):
                return handle_challenges_callback(bot, update)

            # ----- HELP CENTER -----
            if data.startswith("help"):
                return handle_help_callback(bot, update)

            # Fallback
            return safe_edit(bot, update, "⚠️ Unknown action. Tap Menu.", back_to_menu=True)

        # -----------------------------------------
        # HANDLE TEXT COMMANDS
        # -----------------------------------------
        if update.message:

            text = update.message.text or ""
            user_id = update.message.from_user.id

            init_user(user_id)

            # ----- COMMANDS -----
            if text == "/start":
                return handle_menu_command(bot, update)

            if text == "/menu":
                return handle_menu_command(bot, update)

            if text == "/profile":
                return handle_profile_command(bot, update)

            if text == "/help":
                return handle_help_command(bot, update)

            # Default → Send to menu
            return handle_menu_command(bot, update)

    except TelegramError as te:
        logger.error(f"Telegram error: {te}")

    except Exception as e:
        logger.error(f"Router error: {e}")


# ------------------------------------------------------------
# SAFE EDIT HELPERS
# ------------------------------------------------------------
def safe_edit(bot, update, text, back_to_menu=False):
    """Safely edits messages without crashing."""

    try:
        keyboard = None
        if back_to_menu:
            from telegram import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")]
            ])

        update.callback_query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except:
        try:
            bot.send_message(
                chat_id=update.effective_chat.id,
                text=text
            )
        except:
            pass
