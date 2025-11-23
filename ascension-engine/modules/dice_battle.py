"""
modules/dice_battle.py
Dice Battles mini-game for PWN Ascension Engine.

User rolls → Bot rolls → Higher roll wins XP.
"""

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db, save_db
from ui.components import render_text


BATTLE_XP_WIN = 200
BATTLE_XP_LOSE = 50
BATTLE_XP_DRAW = 100


# ---------------------------------------------------------
# UI entry point
# ---------------------------------------------------------
def handle_dice_battle_callback(bot, update):
    query = update.callback_query
    data = query.data

    if data == "dice_start":
        return _start_battle(bot, update)

    if data == "dice_roll":
        return _roll_dice(bot, update)

    if data == "dice_back":
        return _show_menu(bot, update)


# ---------------------------------------------------------
# Show the Dice Battle intro screen
# ---------------------------------------------------------
def _start_battle(bot, update):
    query = update.callback_query
    user = get_user(query.from_user.id)

    text = render_text(user,
        "🎲 *DICE BATTLE*\n\n"
        "Beat the bot in a dice roll.\n"
        "• Win → +200 XP\n"
        "• Draw → +100 XP\n"
        "• Lose → +50 XP\n\n"
        "Ready?"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Roll Dice", callback_data="dice_roll")],
        [InlineKeyboardButton("↩️ Back", callback_data="menu_main")]
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ---------------------------------------------------------
# Roll dice for player + bot
# ---------------------------------------------------------
def _roll_dice(bot, update):
    query = update.callback_query
    user_id = query.from_user.id
    user = get_user(user_id)

    # Player roll
    user_roll = random.randint(1, 6)
    # Bot roll
    bot_roll = random.randint(1, 6)

    text = (
        "🎲 *DICE BATTLE RESULT*\n\n"
        f"👤 You rolled: *{user_roll}*\n"
        f"🤖 Bot rolled: *{bot_roll}*\n\n"
    )

    # Determine result
    db = load_db()
    uid = str(user_id)

    if user_roll > bot_roll:
        text += "🏆 *YOU WIN!* +200 XP"
        db[uid]["xp"] += BATTLE_XP_WIN
    elif user_roll < bot_roll:
        text += "😵 *You lost…* +50 XP"
        db[uid]["xp"] += BATTLE_XP_LOSE
    else:
        text += "🤝 *Draw!* +100 XP"
        db[uid]["xp"] += BATTLE_XP_DRAW

    save_db(db)
    user = get_user(user_id)

    text = render_text(user, text)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Play Again", callback_data="dice_start")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
        [InlineKeyboardButton("🧿 Profile", callback_data="prof_main")],
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ---------------------------------------------------------
# Helper: return to menu
# ---------------------------------------------------------
def _show_menu(bot, update):
    from modules.menu import handle_menu_callback
    return handle_menu_callback(bot, update)
