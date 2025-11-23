"""
modules/bomb_defusal.py
Emoji Bomb Defusal minigame.

User must tap the correct bomb before it "explodes" after a random timer.
"""

import time
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db, save_db
from ui.components import render_text

# XP tiers based on reaction speed
FAST_XP = 200
MID_XP = 120
SLOW_XP = 60
FAIL_XP = 0


# ---------------------------------------------------------
# MAIN CALLBACK HANDLER
# ---------------------------------------------------------
def handle_bomb_defusal_callback(bot, update):
    query = update.callback_query
    data = query.data

    # Open the game intro
    if data == "game_bomb":
        return _show_intro(bot, update)

    # Start the round
    if data == "bomb_start":
        return _start_round(bot, update)

    # Player chooses a bomb
    if data.startswith("bomb_pick_"):
        payload = data.replace("bomb_pick_", "")
        bomb_index_str, start_ts_str, correct_index_str = payload.split("_")
        return _process_choice(bot, update, int(bomb_index_str), float(start_ts_str), int(correct_index_str))


# ---------------------------------------------------------
# INTRO SCREEN
# ---------------------------------------------------------
def _show_intro(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    text = render_text(user,
        "💣 *EMOJI BOMB DEFUSAL*\n\n"
        "Three bombs drop… one is safe.\n"
        "Tap the correct bomb before it explodes!\n\n"
        "• <400ms → +200 XP\n"
        "• <900ms → +120 XP\n"
        "• <1200ms → +60 XP\n"
        "• Wrong bomb / timeout → 0 XP\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💣 Start", callback_data="bomb_start")],
        [InlineKeyboardButton("↩️ Back", callback_data="games_main")]
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ---------------------------------------------------------
# START THE ROUND
# ---------------------------------------------------------
def _start_round(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)
    chat_id = query.message.chat.id
    message_id = query.message.message_id

    # Random explosion delay between 0.8 and 2.0 seconds
    delay = random.uniform(0.8, 2.0)

    # Choose safe bomb index
    correct_index = random.randint(0, 2)

    # Mark start time
    start_ts = time.time()

    # Display bombs
    text = render_text(user,
        "💣💣💣\n\n"
        "Tap *the correct bomb* before it explodes!"
    )

    keyboard = []
    row = []

    for i in range(3):
        row.append(
            InlineKeyboardButton(
                "💣",
                callback_data=f"bomb_pick_{i}_{start_ts}_{correct_index}"
            )
        )

    keyboard.append(row)
    keyboard.append([InlineKeyboardButton("↩️ Back", callback_data="games_main")])

    bot.edit_messag_
