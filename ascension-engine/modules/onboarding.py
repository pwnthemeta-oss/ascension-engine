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
    db[uid][f"onb_step_]()
