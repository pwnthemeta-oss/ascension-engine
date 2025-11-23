"""
modules/activity.py
Scrollable activity log for PWN Ascension Engine.

Supports:
- Paginated activity feed
- Recent actions
- Navigation
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db
from ui.components import render_text


ITEMS_PER_PAGE = 10


# ---------------------------------------------------------
# MAIN UI HANDLER
# ---------------------------------------------------------
def handle_activity_callback(bot, update):
    query = update.callback_query
    data = query.data

    # Format: act_{page_num}
    page = int(data.replace("act_", ""))

    return _show_activity_page(bot, update, page)


# ---------------------------------------------------------
# INTERNAL: RENDER PAGE
# ---------------------------------------------------------
def _show_activity_page(bot, update, page):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)

    db = load_db()
    uid = str(user_id)

    logs = db.get(uid, {}).get("activity", [])

    # Pagination
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = logs[start:end]

    text = "📜 *ACTIVITY LOG*\n\n"
    if not page_items:
        text += "_No activities yet._\n"
    else:
        for item in page_items:
            ts = item["time"]
            msg = item["text"]
            text += f"• `{msg}`\n"

    text = render_text(user, text)

    # Navigation buttons
    nav_buttons = []

    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"act_{page-1}"))
    if end < len(logs):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"act_{page+1}"))

    keyboard = InlineKeyboardMarkup([
        nav_buttons,
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
        [InlineKeyboardButton("🧿 Profile", callback_data="prof_main")]
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
