"""
modules/grind_command.py
Allows user to type /grind and run a grind cycle instantly.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user
from modules.grinding import perform_grind
from ui.components import render_text


def handle_grind_command(bot, update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = get_user(user_id)

    result_type, value = perform_grind(user_id)

    # Cooldown
    if result_type == "cooldown":
        text = render_text(user, f"⏳ *Cooldown Active*\nWait *{value} seconds*.")
        bot.send_message(chat_id, text, parse_mode="Markdown")
        return

    # Badge unlock
    if result_type == "badge":
        text = render_text(user, f"🎖 *BADGE UNLOCKED!*\nYou earned: *{value}*")
        bot.send_message(chat_id, text, parse_mode="Markdown")
        return

    # Rank up
    if result_type == "rankup":
        text = render_text(user, f"🏅 *RANK UP!*\nYou are now *{value}*.")
        bot.send_message(chat_id, text, parse_mode="Markdown")
        return

    # Streak milestone
    if result_type == "streak_milestone":
        text = render_text(user, f"🔥 *STREAK MILESTONE*\nYou've reached *{value} days*!")
        bot.send_message(chat_id, text, parse_mode="Markdown")
        return

    # Success
    text = render_text(user, f"🔥 Grind complete — +50 XP!")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Grind Again", callback_data="prof_grind")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")]
    ])

    bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
