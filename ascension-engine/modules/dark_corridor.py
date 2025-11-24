"""
modules/dark_corridor.py
BALANCED DARK CORRIDOR RNG

Doors:
• Treasure  → small XP gain
• Trap      → small XP loss
• Teleport  → goes deeper
• Secret    → rare tiny bonus

Streak increases difficulty slightly but XP stays controlled.
"""

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db, save_db
from ui.components import render_text


# ---------------------------------------------------------
# Balanced XP values
# ---------------------------------------------------------

TREASURE_MIN = 25
TREASURE_MAX = 75

TRAP_MIN = 5
TRAP_MAX = 20

SECRET_MIN = 10
SECRET_MAX = 35

# Soft multiplier (only slight scaling with streak + depth)
DEPTH_FACTOR = 1.12
STREAK_FACTOR = 0.03  # 3% bonus per streak day


# ---------------------------------------------------------
# Callback handler
# ---------------------------------------------------------
def handle_dark_corridor_callback(bot, update):
    q = update.callback_query
    data = q.data

    if data == "game_corridor":
        return _intro(bot, update)

    if data.startswith("door_pick_"):
        _, _, door_index, depth = data.split("_")
        return _resolve_choice(bot, update, int(door_index), int(depth))


# ---------------------------------------------------------
# Intro screen
# ---------------------------------------------------------
def _intro(bot, update):
    q = update.callback_query
    user = get_user(q.from_user.id)

    text = render_text(user,
        "3️⃣ *DARK CORRIDOR (Balanced Version)*\n\n"
        "Three doors lie ahead...\n\n"
        "🚪  🚪  🚪\n\n"
        "Behind one: *TREASURE* 💰 (+small XP)\n"
        "Behind another: *TRAP* 💀 (small XP loss)\n"
        "The last: *TELEPORT* 🌀 (go deeper)\n\n"
        "Rare chance for a *SECRET ROOM* ✨\n"
        "Streak slightly increases difficulty and reward."
    )

    k = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚪", callback_data="door_pick_0_0"),
            InlineKeyboardButton("🚪", callback_data="door_pick_1_0"),
            InlineKeyboardButton("🚪", callback_data="door_pick_2_0")
        ],
        [InlineKeyboardButton("↩️ Back", callback_data="games_main")]
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=k)


# ---------------------------------------------------------
# Resolve door
# ---------------------------------------------------------
def _resolve_choice(bot, update, door, depth):
    q = update.callback_query
    user_id = q.from_user.id
    user = get_user(user_id)

    db = load_db()
    uid = str(user_id)

    streak = user.get("streak", 0)

    # Slight scaling with depth & streak
    multiplier = (1 + STREAK_FACTOR * streak) * (DEPTH_FACTOR ** depth)

    # Weighted RNG for outcomes
    outcomes = ["treasure", "trap", "teleport"]
    
    # 5% chance for secret event
    if random.random() < 0.05:
        outcomes = ["secret"]
    else:
        random.shuffle(outcomes)

    outcome = outcomes[door] if len(outcomes) > 1 else "secret"

    # -------------------------
    # TREASURE
    # -------------------------
    if outcome == "treasure":
        amount = random.randint(TREASURE_MIN, TREASURE_MAX)
        amount = int(amount * multiplier)

        db[uid]["xp"] += amount
        save_db(db)

        text = render_text(user,
            f"💰 *TREASURE!*\n\n"
            f"You gained +{amount} XP.\n"
