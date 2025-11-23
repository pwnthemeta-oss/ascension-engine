"""
modules/badges.py
Full badge system for PWN Ascension Engine.
Handles:
- Badge definitions
- Unlock conditions
- Progress tracking
- Weekly leaderboard badge
"""

from database import load_db, save_db, get_user


# ---------------------------------------------------------
# BADGE DEFINITIONS
# ---------------------------------------------------------
def get_badge_definitions():
    """Full list of permanent badges in the PWN universe."""
    return {
        "Initiate": {
            "type": "onboarding",
            "required": 1,
            "description": "Complete onboarding."
        },
        "Cracked": {
            "type": "xp",
            "required": 10000,
            "description": "Reach 10,000 XP."
        },
        "Grinder": {
            "type": "daily_grinds",
            "required": 50,
            "description": "Perform 50 grinds in one day."
        },
        "Dominator": {
            "type": "weekly_top3",
            "required": 1,
            "description": "Finish in the weekly Top 3."
        },
        "Keeper": {
            "type": "streak",
            "required": 30,
            "description": "Maintain a 30-day streak."
        },
        "No Life": {
            "type": "xp",
            "required": 100000,
            "description": "Reach 100,000 XP."
        },
        "Trader": {
            "type": "special",
            "required": 1,
            "description": "Quarterly trader badge (manual)."
        },
        "Machine": {
            "type": "special",
            "required": 1,
            "description": "Quarterly grinder badge (manual)."
        },
    }
    

# ---------------------------------------------------------
# PROGRESS DISPLAY HELPER
# ---------------------------------------------------------
def get_badge_progress(user, badge_name):
    """Return text progress for a locked badge."""

    defs = get_badge_definitions()
    badge = defs.get(badge_name)
    if not badge:
        return "Unknown badge"

    btype = badge["type"]
    required = badge["required"]

    if btype == "xp":
        return f"{user.get('xp', 0)}/{required} XP"

    if btype == "streak":
        return f"{user.get('streak', 0)}/{required} days"

    if btype == "daily_grinds":
        return f"{user.get('grinds_today', 0)}/{required} grinds"

    if btype == "weekly_top3":
        return "Finish Top 3 in a weekly leaderboard"

    if btype == "onboarding":
        return "Complete onboarding"

    return "Progress unavailable"


# ---------------------------------------------------------
# CHECK FOR NEW BADGES
# ---------------------------------------------------------
def check_for_new_badges(user_id: int):
    """
    Return badge name if the user unlocked a new badge.
    Called after grind, onboarding, weekly reset, etc.
    """

    db = load_db()
    uid = str(user_id)

    if uid not in db:
        return None

    user = db[uid]
    unlocked = user.get("badges", [])

    defs = get_badge_definitions()

    for name, badge in defs.items():

        # Already unlocked → skip
        if name in unlocked:
            continue

        btype = badge["type"]
        required = badge["required"]

        # ---- CHECK TYPES ----

        # Onboarding
        if btype == "onboarding" and user.get("onboarding_complete"):
            _unlock_badge(user, name, db)
            return name

        # XP
        if btype == "xp" and user.get("xp", 0) >= required:
            _unlock_badge(user, name, db)
            return name

        # Streak
        if btype == "streak" and user.get("streak", 0) >= required:
            _unlock_badge(user, name, db)
            return name

        # Daily grinds
        if btype == "daily_grinds" and user.get("grinds_today", 0) >= required:
            _unlock_badge(user, name, db)
            return name

        # Weekly leaderboard top 3 badge
        if btype == "weekly_top3" and user.get("weekly", {}).get("top3", False):
            _unlock_badge(user, name, db)
            return name

        # Manual special badge (Trader, Machine)
        if btype == "special" and user.get(f"badge_{name.lower()}", False):
            _unlock_badge(user, name, db)
            return name

    # No badges unlocked
    return None


# ---------------------------------------------------------
# INTERNAL: UNLOCK BADGE
# ---------------------------------------------------------
def _unlock_badge(user, badge_name, db):
    """Add badge to user + save."""
    user["badges"].append(badge_name)
    db[str(user["id"])] = user
    save_db(db)
