"""
modules/tap_speed.py
Tap Speed Test mini-game for PWN Ascension Engine.

User must tap within 1 second after receiving a "⚡ TAP NOW!" signal.
"""

import time
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db, save_db
from ui.components import render_text


# XP tiers based on reaction time
XP_FAST = 200      # <0.3s
XP_MEDIUM = 120    # <0.6s
XP_SLOW = 60       # <1.0s
XP_FAIL = 0        # >=1.0s or early tap


# ---------------------------------------------------------
# Callback handler
# ---------------------------------------------------------
def handle_tap_speed_callback(bot, update):
    query = update.callback_query
    data = query.data

    # Show the intro screen
    if data == "game_tapspeed":
        return _show_intro(bot, update)

    # Start the tap test
    if data == "tapspeed_start":
        return _start_test(bot, update)

    # User tapped
    if data.startswith("tapspeed_tap_"):
        timestamp = float(data.replace("tapspeed_tap_", ""))
        return _process_tap(bot, update, timestamp)


# ---------------------------------------------------------
# Intro screen
# ---------------------------------------------------------
def _show_intro(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    text = render_text(user,
        "⚡ *TAP SPEED TEST*\n\n"
        "Tap as fast as possible when the signal appears.\n\n"
        "Rewards:\n"
        "• <300ms → +200 XP\n"
        "• <600ms → +120 XP\n"
        "• <1000ms → +60 XP\n"
        "• Too slow → 0 XP\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Start Test", callback_data="tapspeed_start")],
        [InlineKeyboardButton("↩️ Back", callback_data="games_main")],
    ])

    query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# Start test (waits 1–3 seconds randomly)
# ---------------------------------------------------------
def _start_test(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)
    chat_id = query.message.chat.id

    # Tell user to wait
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=query.message.message_id,
        text=render_text(user, "⏳ Get ready...\n"),
        parse_mode="Markdown",
    )

    # Random wait between 1–3 seconds
    wait = random.uniform(1.5, 3.0)
    time.sleep(wait)

    # Mark timestamp of signal
    signal_ts = time.time()

    # Show TAP NOW with timestamp in callback_data
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ TAP NOW!", callback_data=f"tapspeed_tap_{signal_ts}")]
    ])

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=query.message.message_id,
        text=render_text(user, "⚡ *TAP NOW!*"),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ---------------------------------------------------------
# Process user's tap
# ---------------------------------------------------------
def _process_tap(bot, update, signal_ts):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)

    now = time.time()
    reaction = now - signal_ts

    db = load_db()
    uid = str(user_id)

    # Determine XP
    if reaction < 0:  # tapped before the signal
        xp = XP_FAIL
        msg = "⛔ You tapped too early!"
    elif reaction < 0.3:
        xp = XP_FAST
        msg = f"⚡ *INSANE SPEED!* {int(reaction*1000)}ms (+200 XP)"
    elif reaction < 0.6:
        xp = XP_MEDIUM
        msg = f"🔥 Great reaction! {int(reaction*1000)}ms (+120 XP)"
    elif reaction < 1.0:
        xp = XP_SLOW
        msg = f"👍 Good! {int(reaction*1000)}ms (+60 XP)"
    else:
        xp = XP_FAIL
        msg = f"🐌 Too slow... {int(reaction*1000)}ms (+0 XP)"

    # Apply XP
    db[uid]["xp"] += xp
    save_db(db)
    user = get_user(user_id)

    text = render_text(user, msg)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Play Again", callback_data="tapspeed_start")],
        [InlineKeyboardButton("🎮 Games", callback_data="_]()
