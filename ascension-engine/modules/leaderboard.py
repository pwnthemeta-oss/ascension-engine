"""
modules/leaderboard.py
Weekly leaderboard system (XP, Grinds, Badges).
Tracks:
- Weekly XP rankings
- Weekly Grind rankings
- Badge count rankings
- Weekly reset
- Dominator badge flagging (Top 3)
"""

from datetime import datetime, timedelta
from database import load_db, save_db


# ---------------------------------------------------------
# GET LEADERBOARD: TOP XP
# ---------------------------------------------------------
def get_top_xp():
    db = load_db()
    weekly = {}

    for uid, user in db.items():
        if isinstance(user, dict):
            w = user.get("weekly", {})
            weekly[uid] = w.get("xp", 0)

    sorted_xp = sorted(weekly.items(), key=lambda x: x[1], reverse=True)
    return sorted_xp[:3]


# ---------------------------------------------------------
# GET LEADERBOARD: TOP GRINDS
# ---------------------------------------------------------
def get_top_grinds():
    db = load_db()
    weekly = {}

    for uid, user in db.items():
        if isinstance(user, dict):
            w = user.get("weekly", {})
            weekly[uid] = w.get("grinds", 0)

    sorted_grinds = sorted(weekly.items(), key=lambda x: x[1], reverse=True)
    return sorted_grinds[:3]


# ---------------------------------------------------------
# GET LEADERBOARD: TOP BADGES
# ---------------------------------------------------------
def get_top_badge_collectors():
    db = load_db()
    badge_counts = {}

    for uid, user in db.items():
        if isinstance(user, dict):
            badge_counts[uid] = len(user.get("badges", []))

    sorted_badges = sorted(badge_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_badges[:3]


# ---------------------------------------------------------
# WEEKLY RESET TIME CALCULATOR
# ---------------------------------------------------------
def next_weekly_reset():
    now = datetime.utcnow()
    days_until_monday = (7 - now.weekday()) % 7
    next_mon = now + timedelta(days=days_until_monday)
    reset_time = next_mon.replace(hour=0, minute=0, second=0, microsecond=0)
    return reset_time


# ---------------------------------------------------------
# WEEKLY RESET HANDLER
# ---------------------------------------------------------
def handle_weekly_reset():
    """
    Resets weekly statistics and awards the Dominator flag
    to the Top 3 XP players.
    """

    db = load_db()
    top3 = get_top_xp()

    # Award Dominator badge flag
    for uid, _xp in top3:
        if uid in db:
            db[uid]["weekly"] = db[uid].get("weekly", {})
            db[uid]["weekly"]["top3"] = True  # Badge engine will pick this up

    # Reset all weekly stats
    for uid, user in db.items():
        if isinstance(user, dict):
            user["weekly"] = {
                "xp": 0,
                "grinds": 0,
                "badges": len(user.get("badges", [])),
                "top3": False
            }

    db["next_reset"] = next_weekly_reset().strftime("%Y-%m-%d %H:%M:%S")

    save_db(db)
    return True


# ---------------------------------------------------------
# UI CALLBACK HANDLER (used by router)
# ---------------------------------------------------------
def handle_leaderboard_callback(bot, update):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data == "lb_xp":
        return _show_xp_leaderboard(bot, update)

    elif data == "lb_grinds":
        return _show_grinds_leaderboard(bot, update)

    elif data == "lb_badges":
        return _show_badges_leaderboard(bot, update)


# ---------------------------------------------------------
# INTERNAL: Leaderboard Screens
# ---------------------------------------------------------
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user
from ui.components import render_text


def _show_xp_leaderboard(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    top = get_top_xp()

    text = "🏆 *TOP XP*\n\n"
    rank = 1
    for uid, xp in top:
        text += f"{rank}. `{uid}` — {xp} XP\n"
        rank += 1

    text = render_text(user, text)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔥 Top XP", callback_data="lb_xp"),
            InlineKeyboardButton("⚡ Top Grinds", callback_data="lb_grinds"),
            InlineKeyboardButton("🏅 Top Badges", callback_data="lb_badges"),
        ],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")]
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


def _show_grinds_leaderboard(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    top = get_top_grinds()

    text = "⚡ *TOP GRINDERS*\n\n"
    rank = 1
    for uid, gr in top:
        text += f"{rank}. `{uid}` — {gr} grinds\n"
        rank += 1

    text = render_text(user, text)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔥 Top XP", callback_data="lb_xp"),
            InlineKeyboardButton("⚡ Top Grinds", callback_data="lb_grinds"),
            InlineKeyboardButton("🏅 Top Badges", callback_data="lb_badges"),
        ],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")]
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


def _show_badges_leaderboard(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    top = get_top_badge_collectors()

    text = "🎖 *TOP BADGE COLLECTORS*\n\n"
    rank = 1
    for uid, count in top:
        text += f"{rank}. `{uid}` — {count} badges\n"
        rank += 1

    text = render_text(user, text)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔥 Top XP", callback_data="lb_xp"),
            InlineKeyboardButton("⚡ Top Grinds", callback_data="lb_grinds"),
            InlineKeyboardButton("🏅 Top Badges", callback_data="lb_badges"),
        ],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")]
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
