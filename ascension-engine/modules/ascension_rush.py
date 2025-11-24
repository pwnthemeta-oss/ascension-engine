"""
modules/ascension_rush.py
ASCENSION RUSH — Full Version with 20 custom sequences.

A speed + memory hybrid game:
• Bot flashes emojis rapidly
• User must recall final emoji
• User must recall counts of each emoji
"""

import time
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db, save_db
from ui.components import render_text

# Emojis used in sequences
EMOJIS = ["🔥", "⚡", "💀"]

# XP rewards
XP_CORRECT = 200
XP_PARTIAL = 100
XP_FAIL = 0

# XP penalty for mistakes
RUSH_PENALTY = 8


# ---------------------------------------------
# 20 PREMADE FLASH SEQUENCES
# ---------------------------------------------
FLASH_SEQUENCES = [
    ["🔥", "⚡", "🔥"],
    ["⚡", "💀", "⚡"],
    ["💀", "🔥", "💀"],
    ["⚡", "⚡", "🔥"],
    ["🔥", "💀", "⚡"],

    ["🔥", "⚡", "⚡", "💀"],
    ["💀", "🔥", "🔥", "⚡"],
    ["⚡", "⚡", "💀", "🔥"],
    ["💀", "⚡", "💀", "🔥"],
    ["🔥", "🔥", "⚡", "💀"],

    ["🔥", "⚡", "🔥", "💀", "🔥"],
    ["⚡", "💀", "⚡", "🔥", "⚡"],
    ["💀", "🔥", "💀", "⚡", "💀"],
    ["🔥", "💀", "⚡", "⚡", "🔥"],
    ["⚡", "🔥", "💀", "🔥", "⚡"],

    ["🔥", "⚡", "🔥", "⚡", "💀", "🔥"],
    ["⚡", "💀", "⚡", "🔥", "💀", "⚡"],
    ["💀", "🔥", "💀", "🔥", "⚡", "💀"],
    ["🔥", "🔥", "⚡", "💀", "⚡", "🔥"],
    ["💀", "⚡", "🔥", "⚡", "💀", "🔥"],
]


# ---------------------------------------------------------
# Callback router
# ---------------------------------------------------------
def handle_ascension_rush_callback(bot, update):
    q = update.callback_query
    data = q.data

    if data == "game_rush":
        return _intro(bot, update)

    if data == "rush_start":
        return _start_round(bot, update)

    if data.startswith("rush_answer_"):
        _, answer_type, chosen, correct, counts_raw = data.split("_", 4)
        return _process_answer(bot, update, answer_type, chosen, correct, counts_raw)


# ---------------------------------------------------------
# Intro screen
# ---------------------------------------------------------
def _intro(bot, update):
    q = update.callback_query
    user = get_user(q.from_user.id)

    text = render_text(user,
        "⚡ *ASCENSION RUSH*\n\n"
        "A fast-paced memory challenge.\n"
        "You will see emojis flash rapidly.\n"
        "Then you must answer:\n"
        "• What was the FINAL emoji?\n"
        "• How many of each emoji appeared?\n\n"
        "*Your streak increases difficulty.*"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Start Rush", callback_data="rush_start")],
        [InlineKeyboardButton("↩️ Back", callback_data="games_main")]
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# Generate & flash sequence
# ---------------------------------------------------------
def _start_round(bot, update):
    q = update.callback_query
    user_id = q.from_user.id
    user = get_user(user_id)

    streak = user.get("streak", 0)

    # Higher streak → harder sequence
    max_index = min(4 + streak // 3, len(FLASH_SEQUENCES) - 1)

    # Pick any sequence in difficulty range
    seq = random.choice(FLASH_SEQUENCES[:max_index])

    # Flash sequence FAST
    for emo in seq:
        q.edit_message_text(
            text=render_text(user, emo),
            parse_mode="Markdown"
        )
        time.sleep(0.30)  # flash speed

    # Count emojis
    counts = {e: seq.count(e) for e in EMOJIS}
    final_emoji = seq[-1]

    # Ask for FINAL EMOJI
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(e,
            callback_data=f"rush_answer_final_{e}_{final_emoji}_{counts}"
        ) for e in EMOJIS]
    ])

    q.edit_message_text(
        text=render_text(user, "⚡ *What was the FINAL emoji?*"),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ---------------------------------------------------------
# Process user answers
# ---------------------------------------------------------
def _process_answer(bot, update, answer_type, chosen, correct, counts_raw):
    q = update.callback_query
    user_id = q.from_user.id
    user = get_user(user_id)

    # Parse counts
    counts_raw = counts_raw.replace("{", "").replace("}", "").replace("'", "")
    parts = counts_raw.split(",")
    counts = {}
    for p in parts:
        k, v = p.split(":")
        counts[k.strip()] = int(v.strip())

    db = load_db()
    uid = str(user_id)

    # Correct final emoji?
    if answer_type == "final":
        if chosen == correct:
            # Move to count question
            text = render_text(user,
                f"🔥 Nice! Final emoji was *{correct}*.\n"
                "Now — how many times did each one appear?"
            )

            # Build count questions
            buttons = []
            for e in EMOJIS:
                cb = f"rush_answer_count_{counts[e]}_{counts[e]}_{counts}"
                buttons.append([InlineKeyboardButton(f"{e} = {counts[e]}", callback_data=cb)])

            buttons.append([InlineKeyboardButton("🏠 Menu", callback_data="menu_main")])

            q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
            return
        else:
            db[uid]["xp"] = max(0, db[uid]["xp"] - RUSH_PENALTY)
            save_db(db)

            text = render_text(user, f"💥 WRONG!\nFinal emoji was *{correct}*\n−{RUSH_PENALTY} XP")
            q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=_after_menu())
            return

    # Count question (always correct because choices are exact counts)
    if answer_type == "count":
        db[uid]["xp"] += XP_CORRECT
        save_db(db)

        text = render_text(user,
            f"⚡ *AMAZING MEMORY!*\n"
            f"+{XP_CORRECT} XP"
        )

        q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=_after_menu())


# ---------------------------------------------------------
# After-menu
# ---------------------------------------------------------
def _after_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Play Again", callback_data="rush_start")],
        [InlineKeyboardButton("🎮 Games", callback_data="games_main")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")]
    ])
