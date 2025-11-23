"""
modules/error_screen.py
Global fallback error message UI.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ui.components import render_text
from database import get_user


def show_error(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    text = render_text(user,
        "🟣 *ERROR*\n\n"
        "⚠️ That action is no longer available.\n"
        "Either the session expired or the button was outdated."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Return to Menu", callback_data="menu_main")]
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
