"""
modules/badges.py
Badge UI screens for PWN Ascension Engine.

Includes:
- Badge list screen
- Badge details screen
- Progress bars
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user
from ui.components import render_text
from modules.badges import get_badge_definitions, get_badge_progress


# ---------------------------------------------------------
# MAIN BADGES MENU
# ---------------------------------------------------------
def handle_badges_callback(bot, update):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data == "badge_main":
        return _show_badge_list(bot, update)

    if data.startswith("badge_detail_"):
        badge_name = data.replace("badge_detail_", "")
        return _show_badge_detail(bot, update, badge_name)

    if data == "badge_back":
        return _show_badge_list(bot, update)


# ---------------------------------------------------------
# BADGE LIST SCREEN
# ---------------------------------------------------------
def _show_badge_list(bot, update):
    query = update.callback_query
    user_id = query.from_user.id
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

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ---------------------------------------------------------
# BADGE DETAIL SCREEN
# ---------------------------------------------------------
def _show_badge_detail(bot, update, badge_name):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)
    unlocked = user.get("badges", [])

    defs = get_badge_definitions()
    info = defs.get(badge_name, {})

    title = info.get("title", badge_name)
    desc = info.get("description", "")
    required_type = info.get("type")

    text = f"📜 *{badge_name}*\n\n{desc}\n\n"

    # If unlocked
    if badge_name in unlocked:
        text += "✅ *Unlocked*\n"
    else:
        # Progress display
        progress = get_badge_progress(user, badge_name)
        text += f"Progress: `{progress}`\n"

    text = render_text(user, text)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Back", callback_data="badge_main")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
