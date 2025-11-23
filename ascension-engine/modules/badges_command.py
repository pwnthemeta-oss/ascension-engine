"""
modules/badges_command.py
Allows users to type /badges and open the badge UI instantly.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user
from modules.badges import get_badge_definitions
from ui.components import render_text


def handle_badges_command(bot, update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = get_user(user_id)

    badge_defs = get_badge_definitions()
    unlocked = user.get("badges", [])

    text = "🏅 *YOUR BADGES*\n\n"

    if not unlocked:
        text += "_You haven't unlocked any badges yet._\n"
    else:
        for b in unlocked:
            text += f"🟦 *{b}*\n"

    text = render_text(user, text)

    # Build button grid
    keyboard_rows = []
    for badge_name in badge_defs.keys():
        keyboard_rows.append([
            InlineKeyboardButton(
                badge_name,
                callback_data=f"badge_detail_{badge_name}"
            )
        ])

    keyboard_rows.append([InlineKeyboardButton("🏠 Menu", callback_data="menu_main")])
    keyboard_rows.append([InlineKeyboardButton("🧿 Profile", callback_data="prof_main")])

    keyboard = InlineKeyboardMarkup(keyboard_rows)

    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
