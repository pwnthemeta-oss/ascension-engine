"""
modules/challenges.py
Daily + Weekly challenge system for PWN Ascension.

Handles:
- Challenge definitions
- Progress tracking
- Completion bonuses
- UI rendering
"""

from datetime import datetime
from database import load_db, save_db, get_user
from ui.components import render_text
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ---------------------------------------------------------
# CHALLENGE DEFINITIONS
# ---------------------------------------------------------
def get_challenge_definitions():
    return {
        "daily": {
            "grinds_today": {
                "title": "Grind 20 times today",
                "required": 20,
                "description": "You gain speed, momentum, and discipline.",
                "reward_xp": 200
            },
            "xp_today": {
                "title": "Earn 500 XP today",
                "required": 500,
                "description": "Push yourself past your daily limit.",
                "reward_xp": 300
            },
            "streak_day": {
                "title": "Maintain your streak today",
                "required": 1,
                "description": "Log in and grind at least once today.",
                "reward_xp": 150
            }
        },
        "weekly": {
            "xp_week": {
                "title": "Earn 5,000 XP this week",
                "required": 5000,
                "description": "Only the consistent rise.",
                "reward_xp": 500
            },
            "grinds_week": {
                "title": "Perform 100 grinds this week",
                "required": 100,
                "description": "Prove your dedication.",
                "reward_xp": 600
            },
            "badge_collector": {
                "title": "Unlock a new badge this week",
                "required": 1,
                "description": "Badge collectors dominate the hall of honor.",
                "reward_xp": 300
            }
        }
    }


# ---------------------------------------------------------
# UPDATE CHALLENGE PROGRESS
# (Called by grinding.py)
# ---------------------------------------------------------
def update_challenge_progress(user_id, field, value):
    db = load_db()
    uid = str(user_id)

    if uid not in db:
        return

    user = db[uid]
    challenges = user.setdefault("challenges", {
        "daily": {},
        "weekly": {}
    })

    # Update both daily & weekly if field matches
    if field in challenges["daily"]:
        challenges["daily"][field]["current"] = value

    if field in challenges["weekly"]:
        challenges["weekly"][field]["current"] = value

    save_db(db)


# ---------------------------------------------------------
# UI HANDLER
# ---------------------------------------------------------
def handle_challenges_callback(bot, update):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    user = get_user(user_id)

    if data == "ch_main":
        return _show_challenges(bot, update)

    return query.answer()


# ---------------------------------------------------------
# INTERNAL: RENDER CHALLENGE SCREEN
# ---------------------------------------------------------
def _show_challenges(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)
    db = load_db()

    uid = str(query.from_user.id)
    challenges = db[uid].setdefault("challenges", {"daily": {}, "weekly": {}})

    defs = get_challenge_definitions()

    # Initialize current challenge progress if missing
    for section in ["daily", "weekly"]:
        for cname, c in defs[section].items():
            challenges[section].setdefault(cname, {
                "current": 0,
                "completed": False
            })

    save_db(db)

    # ---- BUILD TEXT ----
    text = "📅 *CHALLENGES*\n\n"

    text += "🔥 *DAILY CHALLENGES*\n"
    for cname, c in defs["daily"].items():
        prog = challenges["daily"][cname]["current"]
        req = c["required"]
        status = "✅ Completed" if prog >= req else f"{prog}/{req}"
        text += f"\n• *{c['title']}*\n  Progress: `{status}`\n"

    text += "\n🏆 *WEEKLY CHALLENGES*\n"
    for cname, c in defs["weekly"].items():
        prog = challenges["weekly"][cname]["current"]
        req = c["required"]
        status = "✅ Completed" if prog >= req else f"{prog}/{req}"
        text += f"\n• *{c['title']}*\n  Progress: `{status}`\n"

    text = render_text(user, text)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
        [InlineKeyboardButton("🧿 Profile", callback_data="prof_main")]
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
