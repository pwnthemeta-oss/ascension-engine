"""
modules/leaderboards_command.py
Allows users to type /leaderboards to instantly open the XP leaderboard.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user
from modules.leaderboard import get_top_xp, get_top_grinds, get_top_badge_collectors
from ui.components import render_text


def handle_leaderboards_command(bot, update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = get_user(user_id)

    # Build XP leaderboard1 as default
    top = get_top_xp()

    text = "🏆 *WEEKLY LEADERBOARDS*\n\n"
    rank = 1
    for uid, xp in top:
        text += f"{rank}. `{uid}` — {xp} XP\n"
        rank += 1

    text = render_text(user, text)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔥 Top XP", callback_data="lb_xp"),
            InlineKeyboardButton("⚡ Top Grinds", callback_data="lb_grinds"),
            InlineKeyboardButton("🏅 Top Badges", callback_data="lb_badges"),
        ],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")]
    ])

    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
