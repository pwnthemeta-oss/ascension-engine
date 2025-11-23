"""
modules/onboarding.py
Handles the full onboarding flow for PWN Ascension.

This module:
- Guides user through multi-step onboarding
- Assigns XP for each step
- Saves onboarding answers
- Unlocks the Initiate badge
- Integrates with UI + grinding + badge system
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import load_db, save_db, get_user
from ui.components import render_text
from modules.badges import check_for_new_badges

# XP gained per onboarding screen
ONBOARDING_XP_REWARD = 100


# ---------------------------------------------------------
# MAIN ENTRY (Triggered by router: "onb_*")
# ---------------------------------------------------------
def handle_onboarding_callback(bot, update):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    user = get_user(user_id)
    step = user.get("onboarding_step", 1)

    # Next button
    if data == "onb_next":
        return _advance_step(bot, update, user_id, user)

    # Answers (A–E) for questions
    if data.startswith("onb_ans_"):
        answer = data.replace("onb_ans_", "")
        return _record_answer(bot, update, user_id, user, answer)

    # Fallback
    return _show_step(bot, update, user_id, user)


# ---------------------------------------------------------
# INTERNAL: Record an answer and move forward
# ---------------------------------------------------------
def _record_answer(bot, update, user_id, user, answer):
    query = update.callback_query

    uid = str(user_id)
    db = load_db()

    # Save user's answer
    step = user.get("onboarding_step", 1)
    db[uid][f"onb_step_{step}_answer"] = answer

    # Give XP
    db[uid]["xp"] = db[uid].get("xp", 0) + ONBOARDING_XP_REWARD

    save_db(db)

    # Next
    user = get_user(user_id)
    return _advance_step(bot, update, user_id, user)


# ---------------------------------------------------------
# INTERNAL: Move to next onboarding screen
# ---------------------------------------------------------
def _advance_step(bot, update, user_id, user):
    query = update.callback_query

    uid = str(user_id)
    db = load_db()

    step = user.get("onboarding_step", 1) + 1
    db[uid]["onboarding_step"] = step
    save_db(db)

    # End of onboarding
    if step > 5:
        db = load_db()
        db[uid]["onboarding_complete"] = True
        save_db(db)

        # Badge check (Initiate)
        new_badge = check_for_new_badges(user_id)

        return _complete_screen(bot, update, user_id)

    return _show_step(bot, update, user_id, get_user(user_id))


# ---------------------------------------------------------
# INTERNAL: Show an onboarding screen by step number
# ---------------------------------------------------------
def _show_step(bot, update, user_id, user):
    query = update.callback_query
    step = user.get("onboarding_step", 1)

    # STEP 1 ----------------------------------------------
    if step == 1:
        text = render_text(user,
            "✨ *CALIBRATION STEP 1*\n\n"
            "What brings you to PWN?\n"
            "Choose the path that fits your vibe. ⚡")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ Start earning XP", callback_data="onb_ans_A")],
            [InlineKeyboardButton("🌐 Join the community", callback_data="onb_ans_B")],
            [InlineKeyboardButton("🏅 Badges & rewards", callback_data="onb_ans_C")],
            [InlineKeyboardButton("🏆 Competition & leaderboards", callback_data="onb_ans_D")],
            [InlineKeyboardButton("🧭 Just exploring", callback_data="onb_ans_E")],
        ])

        return query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    # STEP 2 ----------------------------------------------
    if step == 2:
        text = render_text(user,
            "🔥 *CALIBRATION STEP 2*\n\n"
            "What best describes you?")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Gamer", callback_data="onb_ans_A")],
            [InlineKeyboardButton("🎨 Creator", callback_data="onb_ans_B")],
            [InlineKeyboardButton("📈 Trader", callback_data="onb_ans_C")],
            [InlineKeyboardButton("⚙️ Grinder", callback_data="onb_ans_D")],
        ])

        return query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

    # STEP 3 ----------------------------------------------
    if step == 3:
        text = render_text(user,
            "⚡ *CALIBRATION STEP 3*\n\n"
            "Where do you grind the hardest?")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🖥 PC", callback_data="onb_ans_A")],
            [InlineKeyboardButton("🎮 PlayStation", callback_data="onb_ans_B")],
            [InlineKeyboardButton("🟩 Xbox", callback_data="onb_ans_C")],
            [InlineKeyboardButton("📱 Mobile", callback_data="onb_ans_D")],
            [InlineKeyboardButton("🔴 Nintendo Switch", callback_data="onb_ans_E")],
        ])

        return query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

    # STEP 4 ----------------------------------------------
    if step == 4:
        text = render_text(user,
            "🎯 *CALIBRATION STEP 4*\n\n"
            "What’s your daily grind goal?")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Stack XP", callback_data="onb_ans_A")],
            [InlineKeyboardButton("🔥 Level up fast", callback_data="onb_ans_B")],
            [InlineKeyboardButton("📅 Protect my streak", callback_data="onb_ans_C")],
            [InlineKeyboardButton("🏆 Complete challenges", callback_data="onb_ans_D")],
            [InlineKeyboardButton("👀 Explore and vibe", callback_data="onb_ans_E")],
        ])

        return query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

    # STEP 5 ----------------------------------------------
    if step == 5:
        text = render_text(user,
            "🏁 *FINAL CALIBRATION*\n\n"
            "Are you ready to lock in and grind?")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("LET’S GO! 🏴⚡", callback_data="onb_next")],
            [InlineKeyboardButton("⏳ Give me a minute…", callback_data="onb_next")],
        ])

        return query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# FINAL SCREEN (after step 5)
# ---------------------------------------------------------
def _complete_screen(bot, update, user_id):
    query = update.callback_query
    user = get_user(user_id)

    text = render_text(user,
        "🎉 *ASCENSION ENGINE ACTIVATED!*\n\n"
        "Your calibration is complete — XP, streaks, ranks, badges\n"
        "and your rise through the PWN universe begin NOW. ⚡🌀"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🧿 Open Profile", callback_data="prof_main")],
        [InlineKeyboardButton("🔥 Start Grinding", callback_data="prof_grind")],
        [InlineKeyboardButton("🏅 See Badges", callback_data="badge_main")],
    ])

    query.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
