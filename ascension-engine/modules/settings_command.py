"""
modules/settings_command.py
Allows users to type /settings to instantly open Settings screen.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user
from ui.components import render_text
from modules.settings import _show_settings


def handle_settings_command(bot, update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = get_user(user_id)

    # Directly show settings via inline callback logic
    # (same UI as pressing the Settings button)
    text = render_text(user,
        "⚙️ *SETTINGS*\n\n"
        "Manage your preferences."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Toggle Notifications", callback_data="set_notify")],
        [InlineKeyboardButton("🎨 Toggle Theme", callback_data="set_theme")],
        [InlineKeyboardButton("🌐 Language (soon)", callback_data="set_language")],
        [InlineKeyboardButton("🧹 Reset Data", callback_data="set_reset")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
    ])

    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
