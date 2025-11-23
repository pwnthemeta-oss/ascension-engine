"""
modules/settings.py
User settings panel for PWN Ascension Engine.

Features:
- Notifications ON/OFF
- Theme switch (Dark / Light)
- Language switcher (future)
- Reset data (with confirmation)
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import load_db, save_db, get_user
from ui.components import render_text


# ---------------------------------------------------------
# CALLBACK ENTRY
# ---------------------------------------------------------
def handle_settings_callback(bot, update):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data == "set_main":
        return _show_settings(bot, update)

    if data == "set_notify":
        return _toggle_notifications(bot, update)

    if data == "set_theme":
        return _toggle_theme(bot, update)

    if data == "set_language":
        return _language_stub(bot, update)

    if data == "set_reset":
        return _confirm_reset(bot, update)

    if data == "set_reset_yes":
        return _reset_account(bot, update)

    if data == "set_reset_no":
        return _show_settings(bot, update)


# ---------------------------------------------------------
# MAIN SETTINGS SCREEN
# ---------------------------------------------------------
def _show_settings(bot, update):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)

    notifications = "ON" if user["settings"].get("notifications", True) else "OFF"
    theme = user["settings"].get("theme", "Dark")

    text = render_text(user,
        "⚙️ *SETTINGS*\n\n"
        f"🔔 Notifications: *{notifications}*\n"
        f"🎨 Theme: *{theme}*\n"
        f"🌐 Language: *English*\n"
        "🧹 Reset Data: Clear all progress"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Toggle Notifications", callback_data="set_notify")],
        [InlineKeyboardButton("🎨 Toggle Theme", callback_data="set_theme")],
        [InlineKeyboardButton("🌐 Language (soon)", callback_data="set_language")],
        [InlineKeyboardButton("🧹 Reset Data", callback_data="set_reset")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
    ])

    query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# NOTIFICATION TOGGLE
# ---------------------------------------------------------
def _toggle_notifications(bot, update):
    query = update.callback_query
    user_id = query.from_user.id

    db = load_db()
    uid = str(user_id)

    current = db[uid]["settings"].get("notifications", True)
    db[uid]["settings"]["notifications"] = not current

    save_db(db)

    return _show_settings(bot, update)


# ---------------------------------------------------------
# THEME SWITCHER
# ---------------------------------------------------------
def _toggle_theme(bot, update):
    query = update.callback_query
    user_id = query.from_user.id

    db = load_db()
    uid = str(user_id)

    current = db[uid]["settings"].get("theme", "Dark")
    db[uid]["settings"]["theme"] = "Light" if current == "Dark" else "Dark"

    save_db(db)

    return _show_settings(bot, update)


# ---------------------------------------------------------
# LANGUAGE OPTION (placeholder)
# ---------------------------------------------------------
def _language_stub(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    text = render_text(user,
        "🌐 *LANGUAGE SETTINGS*\n\n"
        "Only English is available right now.\n"
        "More languages coming soon."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data="set_main")]
    ])

    query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# RESET DATA (CONFIRMATION)
# ---------------------------------------------------------
def _confirm_reset(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    text = render_text(user,
        "🧹 *RESET ACCOUNT?*\n\n"
        "This will erase ALL your XP, streak, badges,\n"
        "challenges, weekly stats, and onboarding.\n\n"
        "*This CANNOT be undone.*"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data="set_reset_no"),
         InlineKeyboardButton("✅ Confirm", callback_data="set_reset_yes")],
    ])

    query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# ACTUAL RESET LOGIC
# ---------------------------------------------------------
def _reset_account(bot, update):
    query = update.callback_query
    user_id = query.from_user.id

    uid = str(user_id)
    db = load_db()

    # Full wipe of user data
    db[uid] = {
        "xp": 0,
        "rank": "Bronze",
        "streak": 0,
        "grinds_today": 0,
        "last_grind": 0,
        "last_grind_date": None,
        "badges": [],
        "onboarding_step": 1,
        "onboarding_complete": False,
        "settings": {
            "notifications": True,
            "theme": "Dark",
            "language": "English"
        },
        "activity": [],
        "weekly": {
            "xp": 0,
            "grinds": 0,
            "badges": 0,
            "top3": False
        },
    }

    save_db(db)

    text = render_text(get_user(user_id),
        "🧹 *ACCOUNT RESET SUCCESSFUL*\n\n"
        "You are brand new.\n"
        "Start fresh and rise again. ⚡"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
        [InlineKeyboardButton("🧿 Profile", callback_data="prof_main")],
    ])

    query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)
