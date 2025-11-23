import os
import json
import time

# Storage folder
STORAGE_DIR = "storage"
DB_PATH = os.path.join(STORAGE_DIR, "database.json")


# -------------------------------
# Ensure storage folder exists
# -------------------------------
os.makedirs(STORAGE_DIR, exist_ok=True)

# If JSON database does not exist → create empty
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump({}, f, indent=4)


# -------------------------------
# LOAD DATABASE
# -------------------------------
def load_db():
    """Load and return entire JSON database."""
    try:
        with open(DB_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


# -------------------------------
# SAVE DATABASE
# -------------------------------
def save_db(db: dict):
    """Safely write the database to disk."""
    # Write to temporary file first (prevents corruption)
    temp_path = DB_PATH + ".tmp"

    with open(temp_path, "w") as f:
        json.dump(db, f, indent=4)

    # Replace the old file atomically
    os.replace(temp_path, DB_PATH)


# -------------------------------
# INIT USER IF MISSING
# -------------------------------
def init_user(user_id: int):
    """Create a new user entry if they don't exist yet."""
    uid = str(user_id)
    db = load_db()

    if uid not in db:
        db[uid] = {
            "xp": 0,
            "rank": "Bronze",
            "streak": 0,
            "grinds_today": 0,
            "last_grind": 0,
            "last_grind_date": None,
            "badges": [],
            "onboarding_step": 1,
            "onboarding_complete": False,
            "settings": {
                "notifications": True,
                "theme": "Dark",
                "language": "English"
            },
            "activity": [],
            "weekly": {
                "xp": 0,
                "grinds": 0,
                "badges": 0
            },
            "created_at": int(time.time())
        }
        save_db(db)

    return load_db()[uid]


# -------------------------------
# ACTIVITY LOGGING
# -------------------------------
def log_activity(user_id: int, text: str):
    """Add an entry to user's activity log."""
    db = load_db()
    uid = str(user_id)

    if uid not in db:
        init_user(user_id)
        db = load_db()

    log_list = db[uid].setdefault("activity", [])
    log_list.insert(0, {
        "time": int(time.time()),
        "text": text
    })

    # Limit to last 500 entries
    db[uid]["activity"] = log_list[:500]

    save_db(db)


# -------------------------------
# GET USER OBJECT
# -------------------------------
def get_user(user_id: int):
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        return init_user(user_id)
    return db[uid]
