"""
modules/help_center.py
Full HELP screen for PWN Ascension Engine.

Provides:
- /help command
- Commands list
- System explanation
- Contact admin button
- Back to menu
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ui.components import render_text
from database import get_user


# ---------------------------------------------------------
# /help typed command
# ---------------------------------------------------------
def handle_help_command(bot, update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = get_user(user_id)
    text, keyboard = _help_text_and_keyboard(user)

    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ---------------------------------------------------------
# Callback handler
# ---------------------------------------------------------
def handle_help_callback(bot, update):
    query = update.callback_query
    user_id = query.from_user.id

    user = get_user(user_id)
    text, keyboard = _help_text_and_keyboard(user)

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ---------------------------------------------------------
# INTERNAL: HELP screen template
# ---------------------------------------------------------
def _help_text_and_keyboard(user):
    text = (
        "❓ *HELP & COMMANDS*\n\n"
        "Welcome to the PWN Ascension Engine.\n"
        "Here’s everything you need to navigate the universe:\n\n"
        "📜 *Commands*\n"
        "/start — Begin your journey\n"
        "/menu — Open main menu\n"
        "/profile — View your stats\n"
        "/grind — Gain XP\n"
        "/leaderboards — Weekly top ranks\n"
        "/badges — Your achievements\n"
        "/settings — Personalize your engine\n"
        "/help — This help center\n\n"
        "🔥 *How it Works*\n"
        "• XP powers your rise\n"
        "• Streaks reward consistency\n"
        "• Grinding earns XP every cooldown\n"
        "• Ranks unlock automatically\n"
        "• Badges mark your milestones\n"
        "• Weekly leaderboards reset every Monday\n"
        "• Challenges boost your progression\n"
    )

    text = render_text(user, text)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Contact Admin", url="https://t.me/YourAdminUsername")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")]
    ])

    return text, keyboard
