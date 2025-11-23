"""
modules/grinding.py
Grinding engine for PWN Ascension — Replit sync version.
Handles:
- XP gain
- Cooldowns
- Daily reset
- Streak system
- Rank progression
- Badge unlocks
- Weekly counters
- Challenge updates
"""

import time
from datetime import datetime

from database import get_user, save_db, load_db, log_activity
from modules.badges import check_for_new_badges
from modules.challenges import update_challenge_progress


COOLDOWN_SECONDS = 30        # Time between allowed grinds
GRIND_XP = 50                # XP gained each grind
STREAK_MILESTONES = [5, 10, 20, 30]


# ---------------------------------------------------------
# MAIN GRIND FUNCTION
# ---------------------------------------------------------
def perform_grind(user_id: int):
    """
    Returns:
      ("cooldown", seconds_left)
      ("badge", badge_name)
      ("rankup", new_rank)
      ("streak_milestone", streak_days)
      ("success", xp_gain)
    """

    db = load_db()
    uid = str(user_id)

    if uid not in db:
        user = get_user(user_id)
        db = load_db()
    else:
        user = db[uid]

    now = datetime.utcnow()
    now_ts = time.time()

    last_ts = user.get("last_grind", 0)
    diff = now_ts - last_ts

    # -----------------------------------------
    # COOLDOWN CHECK
    # -----------------------------------------
    if diff < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - int(diff)
        return ("cooldown", remaining)

    # -----------------------------------------
    # DAILY RESET
    # -----------------------------------------
    today_str = now.strftime("%Y-%m-%d")
    last_date = user.get("last_grind_date")

    if last_date != today_str:
        # New day, reset daily counters
        user["grinds_today"] = 0
        user["xp_today"] = 0

        # Determine streak:
        # If last grind was yesterday → continue streak
        if last_date:
            try:
                last_date_dt = datetime.strptime(last_date, "%Y-%m-%d")
                if (now - last_date_dt).days == 1:
                    user["streak"] += 1
                else:
                    user["streak"] = 1
            except:
                user["streak"] = 1
        else:
            user["streak"] = 1

        user["last_grind_date"] = today_str

    # -----------------------------------------
    # APPLY GRIND
    # -----------------------------------------
    user["grinds_today"] += 1
    user["last_grind"] = now_ts
    user["xp"] += GRIND_XP
    user["xp_today"] = user.get("xp_today", 0) + GRIND_XP

    # WEEKLY COUNTERS
    weekly = user.get("weekly", {})
    weekly["xp"] = weekly.get("xp", 0) + GRIND_XP
    weekly["grinds"] = weekly.get("grinds", 0) + 1
    user["weekly"] = weekly

    # Log activity
    log_activity(user_id, f"Performed grind (+{GRIND_XP} XP)")

    # -----------------------------------------
    # CHALLENGES UPDATE
    # -----------------------------------------
    update_challenge_progress(user_id, "grinds_today", user["grinds_today"])
    update_challenge_progress(user_id, "xp_today", user["xp_today"])
    update_challenge_progress(user_id, "xp_week", weekly["xp"])
    update_challenge_progress(user_id, "grinds_week", weekly["grinds"])

    save_db(db)

    # -----------------------------------------
    # BADGE CHECK
    # -----------------------------------------
    new_badge = check_for_new_badges(user_id)
    if new_badge:
        return ("badge", new_badge)

    # -----------------------------------------
    # STREAK MILESTONE
    # -----------------------------------------
    if user["streak"] in STREAK_MILESTONES:
        save_db(db)
        return ("streak_milestone", user["streak"])

    # -----------------------------------------
    # RANK PROGRESSION
    # -----------------------------------------
    new_rank = _calculate_rank(user["xp"])
    if new_rank != user.get("rank"):
        user["rank"] = new_rank
        save_db(db)
        return ("rankup", new_rank)

    save_db(db)
    return ("success", GRIND_XP)


# ---------------------------------------------------------
# INTERNAL: RANK CALCULATION
# ---------------------------------------------------------
def _calculate_rank(xp):
    """Return the appropriate rank based on XP."""
    if xp >= 10000:
        return "Ascended"
    if xp >= 5000:
        return "Master"
    if xp >= 2500:
        return "Diamond"
    if xp >= 1500:
        return "Gold"
    if xp >= 750:
        return "Silver"
    return "Bronze"
