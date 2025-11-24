"""
modules/corrupted_oracle.py
CORRUPTED ORACLE — Prediction Game

Bot shows a number (1–12).
User predicts: Higher / Lower / Same.
XP varies by difficulty.
"""

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db, save_db
from ui.components import render_text

XP_SAME = 200      # Hardest prediction
XP_NORMAL = 100    # Higher / Lower correct
XP_WRONG = 15      # Penalty


# ---------------------------------------------------------
# Callback Handler
# ---------------------------------------------------------
def handle_oracle_callback(bot, update):
    q = update.callback_query
    data = q.data

    if data == "game_oracle":
        return intro_screen(bot, update)

    if data.startswith("oracle_guess_"):
        _, _, guess, original = data.split("_")
        return process_guess(bot, update, guess, int(original))


# ---------------------------------------------------------
# Intro screen
# ---------------------------------------------------------
def intro_screen(bot, update):
    q = update.callback_query
    user = get_user(q.from_user.id)

    number = random.randint(1, 12)

    text = render_text(
        user,
        f"🔮 *CORRUPTED ORACLE*\n\n"
        f"The Oracle reveals a number:\n\n"
        f"✨ **{number}** ✨\n\n"
        "Predict the future:\n"
        "🔼 Higher\n"
        "🔽 Lower\n"
        "🟰 Same\n\n"
        "Correct Same = **+200 XP** (hard)\n"
        "Correct High/Low = **+100 XP**\n"
        "Wrong = **–15 XP**"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔼 Higher", callback_data=f"oracle_guess_higher_{number}"),
            InlineKeyboardButton("🟰 Same", callback_data=f"oracle_guess_same_{number}"),
            InlineKeyboardButton("🔽 Lower", callback_data=f"oracle_guess_lower_{number}"),
        ],
        [InlineKeyboardButton("↩️ Back", callback_data="games_main")]
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# Process Guess
# ---------------------------------------------------------
def process_guess(bot, update, guess, original):
    q = update.callback_query
    user_id = q.from_user.id
    user = get_user(user_id)

    new_number = random.randint(1, 12)

    db = load_db()
    uid = str(user_id)

    # Determine if correct
    if new_number == original and guess == "same":
        # Hardest case
        db[uid]["xp"] += XP_SAME
        save_db(db)
        result = render_text(
            user,
            f"✨ *THE ORACLE SPEAKS...*\n\n"
            f"Original: {original}\n"
            f"New: {new_number}\n\n"
            f"🟰 You predicted *SAME* — **CORRECT!**\n"
            f"+{XP_SAME} XP"
        )

    elif new_number > original and guess == "higher":
        db[uid]["xp"] += XP_NORMAL
        save_db(db)
        result = render_text(
            user,
            f"🔼 *CORRECT PREDICTION!*\n\n"
            f"Original: {original}\n"
            f"New: {new_number}\n\n"
            f"+{XP_NORMAL} XP"
        )

    elif new_number < original and guess == "lower":
        db[uid]["xp"] += XP_NORMAL
        save_db(db)
        result = render_text(
            user,
            f"🔽 *CORRECT PREDICTION!*\n\n"
            f"Original: {original}\n"
            f"New: {new_number}\n\n"
            f"+{XP_NORMAL} XP"
        )

    else:
        # Wrong prediction
        db[uid]["xp"] = max(0, db[uid]["xp"] - XP_WRONG)
        save_db(db)
        result = render_text(
            user,
            f"💀 *THE ORACLE LAUGHS... WRONG!* 💀\n\n"
            f"Original: {original}\n"
            f"New: {new_number}\n\n"
            f"Penalty: −{XP_WRONG} XP"
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔮 Play Again", callback_data="game_oracle")],
        [InlineKeyboardButton("🎮 Games", callback_data="games_main")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
    ])

    q.edit_message_text(text=result, parse_mode="Markdown", reply_markup=keyboard)
