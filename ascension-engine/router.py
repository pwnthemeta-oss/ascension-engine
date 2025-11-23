"""
router.py
Unified router for ALL Telegram updates (messages + callbacks)
FULL VERSION WITH ALL COMMAND HANDLERS
"""

import logging
from telegram import Update
from telegram.error import TelegramError

# Core screens
from modules.start import handle_start_command
from modules.menu import handle_menu_command, handle_menu_callback
from modules.profile import handle_profile_callback, handle_profile_command
from modules.help_center import handle_help_command, handle_help_callback
from modules.error_screen import show_error

# Grind
from modules.grind_command import handle_grind_command
from modules.grinding import handle_grind_callback

# Badges
from modules.badges_command import handle_badges_command
from modules.badges import handle_badges_callback

# Leaderboards
from modules.leaderboards_command import handle_leaderboards_command
from modules.leaderboard import handle_leaderboard_callback

# Settings
from modules.settings_command import handle_settings_command
from modules.settings import handle_settings_callback

# Activity
from modules.activity_command import handle_activity_command
from modules.activity import handle_activity_callback

# Challenges
from modules.challenges import handle_challenges_callback

# Onboarding
from modules.onboarding import handle_onboarding_callback

# Database
from database import init_user

logger = logging.getLogger(__name__)


# ------------------------------------------------------
# MAIN ROUTER ENTRY
# ------------------------------------------------------
def handle_update(bot, update: Update):

    try:
        # Ignore empty updates
        if not update:
            return

        # =====================================================
        # CALLBACK QUERY (inline button presses)
        # =====================================================
        if update.callback_query:
            data = update.callback_query.data
            user_id = update.callback_query.from_user.id

            init_user(user_id)  # ensure user exists

            # ----- MENU -----
            if data.startswith("menu"):
                return handle_menu_callback(bot, update)

            # ----- PROFILE -----
            if data.startswith("prof"):
                return handle_profile_callback(bot, update)

            # ----- GRIND -----
            if data.startswith("grind"):
                return handle_grind_callback(bot, update)

            # ----- BADGES -----
            if data.startswith("badge"):
                return handle_badges_callback(bot, update)

            # ----- LEADERBOARD -----
            if data.startswith("lb_"):
                return handle_leaderboard_callback(bot, update)

            # ----- SETTINGS -----
            if data.startswith("set_"):
                return handle_settings_callback(bot, update)

            # ----- ACTIVITY -----
            if data.startswith("act_"):
                return handle_activity_callback(bot, update)

            # ----- CHALLENGES -----
            if data.startswith("ch_"):
                return handle_challenges_callback(bot, update)

            # ----- ONBOARDING -----
            if data.startswith("onb_"):
                return handle_onboarding_callback(bot, update)

            # ----- HELP -----
            if data.startswith("help"):
                return handle_help_callback(bot, update)

            # Otherwise → error
            return show_error(bot, update)

        # =====================================================
        # MESSAGE HANDLING (commands)
        # =====================================================
        if update.message:
            text = update.message.text or ""
            user_id = update.message.from_user.id
            init_user(user_id)

            # ----- COMMANDS -----
            if text == "/start":
                return handle_start_command(bot, update)

            if text == "/menu":
                return handle_menu_command(bot, update)

            if text == "/profile":
                return handle_profile_command(bot, update)

            if text == "/help":
                return handle_help_command(bot, update)

            if text == "/grind":
                return handle_grind_command(bot, update)

            if text == "/badges":
                return handle_badges_command(bot, update)

            if text == "/leaderboards":
                return handle_leaderboards_command(bot, update)

            if text == "/settings":
                return handle_settings_command(bot, update)

            if text == "/activity":
                return handle_activity_command(bot, update)

            # Default → open menu
            return handle_menu_command(bot, update)

    except TelegramError as te:
        logger.error(f"Telegram error: {te}")
    except Exception as e:
        logger.error(f"Router error: {e}")
