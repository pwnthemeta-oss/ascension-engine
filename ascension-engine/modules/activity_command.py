"""
modules/activity_command.py
Allows users to type /activity and instantly open the activity log.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user
from ui.components import render_text
from database import load_db


ITEMS_PER_PAGE = 10


def handle_activity_command(bot, update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = get_user(user_id)
    db = load_db()
    uid = str(user_id)

    logs = db.get(uid, {}).get("activity", [])
    page = 0

    # First page
    start = 0
    end = ITEMS_PER_PAGE
    page_items = logs[start:end]

    text = "📜 *ACTIVITY LOG*\n\n"

    if not page_items:
        text += "_You have no activity yet._"
    else:
        for item in page_items:
            msg = item["text"]
            text += f"• `{msg}`\n"

    text = render_text(user, text)

    # Navigation buttons
    nav_buttons = []
    if end < len(logs):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data="act_1"))

    keyboard = InlineKeyboardMarkup([
        nav_buttons,
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
        [InlineKeyboardButton("🧿 Profile", callback_data="prof_main")]
    ])

    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
