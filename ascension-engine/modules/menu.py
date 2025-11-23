"""
modules/menu.py
Main Menu screen + /menu command
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user
from ui.components import render_text


# ----------------------------------------------------
# /menu command
# ----------------------------------------------------
def handle_menu_command(bot, update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = get_user(user_id)
    text = render_text(
        user,
        "🏠 *MAIN MENU*\n\n"
        "Your command center for the PWN Ascension Engine.\n"
        "Choose where to go next."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧿 Profile", callback_data="prof_main")],
        [InlineKeyboardButton("🔥 Grind", callback_data="prof_grind")],
        [InlineKeyboardButton("🏅 Badges", callback_data="badge_main")],
        [InlineKeyboardButton("🏆 Leaderboards", callback_data="lb_xp")],
        [InlineKeyboardButton("📅 Challenges", callback_data="ch_main")],
        [InlineKeyboardButton("❓ Help", callback_data="help_main")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="set_main")],
    ])

    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ----------------------------------------------------
# Menu button callback
# ----------------------------------------------------
def handle_menu_callback(bot, update):
    query = update.callback_query
    user_id = query.from_user.id

    user = get_user(user_id)

    text = render_text(
        user,
        "🏠 *MAIN MENU*\n\n"
        "Your command center for the PWN Ascension Engine.\n"
        "Choose where to go next."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧿 Profile", callback_data="prof_main")],
        [InlineKeyboardButton("🔥 Grind", callback_data="prof_grind")],
        [InlineKeyboardButton("🏅 Badges", callback_data="badge_main")],
        [InlineKeyboardButton("🏆 Leaderboards", callback_data="lb_xp")],
        [InlineKeyboardButton("📅 Challenges", callback_data="ch_main")],
        [InlineKeyboardButton("❓ Help", callback_data="help_main")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="set_main")],
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
