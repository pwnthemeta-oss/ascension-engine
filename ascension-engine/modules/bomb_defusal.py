"""
modules/bomb_defusal.py
Emoji Bomb Defusal — NEW VERSION

User must tap the *one bomb that will NOT explode*.
No timer. No reaction speed.
Purely a guessing / logic mini-game.
"""

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db, save_db
from ui.components import render_text

# XP rewards
SAFE_XP = 150
FAIL_XP = 0


# ---------------------------------------------------------
# Callback handler
# ---------------------------------------------------------
def handle_bomb_defusal_callback(bot, update):
    query = update.callback_query
    data = query.data

    if data == "game_bomb":
        return _show_intro(bot, update)

    if data == "bomb_start":
        return _start_round(bot, update)

    if data.startswith("bomb_pick_"):
        chosen, correct = data.replace("bomb_pick_", "").split("_")
        return _process_choice(bot, update, int(chosen), int(correct))


# ---------------------------------------------------------
# Intro screen
# ---------------------------------------------------------
def _show_intro(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    text = render_text(user,
        "💣 *EMOJI BOMB DEFUSAL*\n\n"
        "Three bombs. Two will explode. One is safe.\n"
        "Choose the bomb that will NOT explode.\n\n"
        "• Safe choice → +150 XP\n"
        "• Wrong choice → 💥 Boom\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💣 Start Game", callback_data="bomb_start")],
        [InlineKeyboardButton("↩️ Back", callback_data="games_main")],
    ])

    query.edit_message_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )


# ---------------------------------------------------------
# Start round (no timer)
# ---------------------------------------------------------
def _start_round(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    # Pick safe bomb index
    safe_index = random.randint(0, 2)

    text = render_text(user,
        "💣💣💣\n\n"
        "Pick the bomb that will NOT explode!"
    )

    keyboard = []
    row = []

    for i in range(3):
        row.append(
            InlineKeyboardButton(
                "💣",
                callback_data=f"bomb_pick_{i}_{safe_index}"
            )
        )

    keyboard.append(row)
    keyboard.append([InlineKeyboardButton("↩️ Back", callback_data="games_main")])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------------------------------------------------
# Process user selection
# ---------------------------------------------------------
def _process_choice(bot, update, chosen, safe_index):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)

    db = load_db()
    uid = str(user_id)

    # Correct?
    else:
    # WRONG BOMB → Lose 5 XP (but never go below 0)
    current_xp = db[uid].get("xp", 0)
    new_xp = max(0, current_xp - 5)
    db[uid]["xp"] = new_xp
    save_db(db)

    text = render_text(user,
        "💥 *BOOM!*\n\n"
        "You picked an exploding bomb.\n"
        "−5 XP"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Play Again", callback_data="bomb_start")],
        [InlineKeyboardButton("🎮 Games", callback_data="games_main")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
