"""
modules/xp_typhoon.py
XP TYPHOON — Tap Survival Game

Goal:
• User taps as fast as possible during a storm
• More taps = more XP
• Storm lasts 5 seconds
"""

import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db, save_db
from ui.components import render_text

STORM_DURATION = 5        # seconds
XP_PER_TAP = 4            # XP awarded per tap
PENALTY_SMALL = 5         # XP loss if < 3 taps


# ---------------------------------------------------------
# Callback Handler
# ---------------------------------------------------------
def handle_typhoon_callback(bot, update):
    q = update.callback_query
    data = q.data

    if data == "game_typhoon":
        return intro_screen(bot, update)

    if data.startswith("typhoon_start_"):
        _, _, tcount = data.split("_")
        return typhoon_tap(bot, update, int(tcount))

    if data.startswith("typhoon_done_"):
        _, _, taps = data.split("_")
        return typhoon_finish(bot, update, int(taps))


# ---------------------------------------------------------
# Intro Screen
# ---------------------------------------------------------
def intro_screen(bot, update):
    q = update.callback_query
    user = get_user(q.from_user.id)

    text = render_text(user,
        "🌪️ *XP TYPHOON — SURVIVAL MODE* 🌪️\n\n"
        "Tap as fast as you can to resist the storm!\n"
        f"You have *{STORM_DURATION} seconds*.\n\n"
        "🔥 More taps = More XP\n"
        "💀 Weak tapping = XP penalty\n\n"
        "Ready?"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌪️ START TYPHOON", callback_data="typhoon_start_0")],
        [InlineKeyboardButton("↩️ Back", callback_data="games_main")]
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# Tap Handler
# ---------------------------------------------------------
def typhoon_tap(bot, update, taps):
    q = update.callback_query
    user = get_user(q.from_user.id)

    taps += 1  # user tapped one more time

    text = render_text(user,
        "🌪️ *TAP TO STAY IN THE STORM!* 🌪️\n"
        f"Taps: *{taps}*\n\n"
        "Keep tapping! The typhoon rages…"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ TAP", callback_data=f"typhoon_start_{taps}")],
        [InlineKeyboardButton("Stop", callback_data=f"typhoon_done_{taps}")]
    ])

    q.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ---------------------------------------------------------
# Storm ends — give XP
# ---------------------------------------------------------
def typhoon_finish(bot, update, taps):
    q = update.callback_query
    user_id = q.from_user.id
    user = get_user(user_id)

    db = load_db()
    uid = str(user_id)

    # XP Calculation
    if taps < 3:
        db[uid]["xp"] = max(0, db[uid]["xp"] - PENALTY_SMALL)
        save_db(db)
        result = render_text(user,
            f"💀 *TYPHOON OVERPOWERED YOU!*\n\n"
            f"You tapped only *{taps}* times.\n"
            f"Penalty: −{PENALTY_SMALL} XP"
        )
    else:
        gained = taps * XP_PER_TAP
        db[uid]["xp"] += gained
        save_db(db)
        result = render_text(user,
            f"🔥 *YOU SURVIVED THE TYPHOON!* 🔥\n\n"
            f"Taps: *{taps}*\n"
            f"XP Earned: *+{gained} XP*"
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Play Again", callback_data="typhoon_start_0")],
        [InlineKeyboardButton("🎮 Games", callback_data="games_main")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
    ])

    q.edit_message_text(result, parse_mode="Markdown", reply_markup=keyboard)
