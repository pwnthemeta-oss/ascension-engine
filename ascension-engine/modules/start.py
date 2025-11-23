"""
modules/start.py
Handles /start command + first-time welcome screen.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import init_user, get_user
from ui.components import render_text


# ---------------------------------------------------------
# /start COMMAND
# ---------------------------------------------------------
def handle_start_command(bot, update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    init_user(user_id)
    user = get_user(user_id)

    text = render_text(user,
        "🔥 *WELCOME TO PWN ASCENSION* 🔥\n\n"
        "Where every action lifts you higher. 🌀\n"
        "You’ve awakened the Ascension Engine — your XP reactor, rank booster, streak multiplier, and power core.\n\n"
        "This isn’t just a bot…\n"
        "This is your evolution machine. 🚀\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔵 Begin Ascension", callback_data="onb_next")],
        [InlineKeyboardButton("🌀 What is PWN?", callback_data="help_main")],
        [InlineKeyboardButton("🏆 Leaderboards", callback_data="lb_xp")],
        [InlineKeyboardButton("🧿 My Profile", callback_data="prof_main")],
    ])

    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
