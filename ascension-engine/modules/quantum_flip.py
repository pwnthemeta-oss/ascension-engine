"""
modules/quantum_flip.py
QUANTUM FLIP — 50/50 Chaos Game

Outcomes:
• Heads = XP gain
• Tails = XP loss
• Edge (1%) = Massive XP + Rare Badge
"""

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db, save_db
from ui.components import render_text

XP_HEADS = 100
XP_TAILS = 20
XP_EDGE = 500

RARE_BADGE_NAME = "Quantum Master"


# ---------------------------------------------------------
# Callback Handler
# ---------------------------------------------------------
def handle_quantum_callback(bot, update):
    q = update.callback_query
    data = q.data

    if data == "game_quantum":
        return intro(bot, update)

    if data == "quantum_flip":
        return flip(bot, update)


# ---------------------------------------------------------
# Intro Screen
# ---------------------------------------------------------
def intro(bot, update):
    q = update.callback_query
    user = get_user(q.from_user.id)

    text = render_text(
        user,
        "⚛️ *QUANTUM FLIP — CHAOS GAME* ⚛️\n\n"
        "Flip the quantum coin:\n"
        "• ⚛️ *Heads* → +100 XP\n"
        "• ⚛️ *Tails* → −20 XP\n"
        "• ⚛️ *Edge (1%)* → +500 XP + Rare Badge\n\n"
        "Are you ready for pure RNG?"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚛️ FLIP COIN", callback_data="quantum_flip")],
        [InlineKeyboardButton("↩️ Back", callback_data="games_main")]
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# Process Coin Flip
# ---------------------------------------------------------
def flip(bot, update):
    q = update.callback_query
    user_id = q.from_user.id
    user = get_user(user_id)

    db = load_db()
    uid = str(user_id)

    # 1% chance Edge
    edge_roll = random.random() < 0.01

    if edge_roll:
        db[uid]["xp"] += XP_EDGE

        # Award rare badge if not already unlocked
        if RARE_BADGE_NAME not in db[uid]["badges"]:
            db[uid]["badges"].append(RARE_BADGE_NAME)

        save_db(db)

        text = render_text(
            user,
            "⚛️✨ *INCREDIBLE! THE COIN LANDED ON ITS EDGE!* ✨⚛️\n\n"
            f"You gained *+{XP_EDGE} XP*.\n"
            f"🎖️ Rare Badge Unlocked: *{RARE_BADGE_NAME}*"
        )

    else:
        # 50/50 Heads or Tails
        outcome = random.choice(["heads", "tails"])

        if outcome == "heads":
            db[uid]["xp"] += XP_HEADS
            save_db(db)

            text = render_text(
                user,
                "⚛️ *HEADS!* ⚛️\n\n"
                f"You gained +{XP_HEADS} XP!"
            )

        else:
            db[uid]["xp"] = max(0, db[uid]["xp"] - XP_TAILS)
            save_db(db)

            text = render_text(
                user,
                "⚛️ *TAILS!* ⚛️\n\n"
                f"You lost −{XP_TAILS} XP!"
            )

    # Replay menu
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚛️ Flip Again", callback_data="quantum_flip")],
        [InlineKeyboardButton("🎮 Games", callback_data="games_main")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)
