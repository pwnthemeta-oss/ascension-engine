"""
ui/components.py
Shared UI components, theme renderer, and text formatting utilities.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ---------------------------------------------------------
# DARK THEME RENDERER
# ---------------------------------------------------------
def render_dark(text: str) -> str:
    """Apply Dark theme styling (default)."""
    return (
        "🌑 *DARK MODE*\n"
        + text
    )


# ---------------------------------------------------------
# LIGHT THEME RENDERER
# ---------------------------------------------------------
def render_light(text: str) -> str:
    """Apply Light theme styling (emoji-shifted)."""
    return (
        "🌕 *LIGHT MODE*\n"
        + text.replace("🔥", "✨")
              .replace("⚡", "💡")
              .replace("🏅", "🎖")
              .replace("💠", "🔷")
    )


# ---------------------------------------------------------
# MAIN THEME RENDER ENTRY
# ---------------------------------------------------------
def render_text(user: dict, text: str) -> str:
    """
    Returns themed text depending on user's settings.
    Defaults to Dark Mode.
    """
    settings = user.get("settings", {})
    theme = settings.get("theme", "Dark")

    if theme == "Light":
        return render_light(text)

    return render_dark(text)


# ---------------------------------------------------------
# SAFE INLINE KEYBOARD BUILDER
# ---------------------------------------------------------
def build_keyboard(rows):
    """
    Build an InlineKeyboardMarkup from a list of lists:

    Example:
    build_keyboard([
        [("Button 1", "cb_1")],
        [("Button 2", "cb_2"), ("Button 3", "cb_3")]
    ])
    """

    keyboard = []

    for row in rows:
        btn_row = []
        for btn_text, callback in row:
            btn_row.append(InlineKeyboardButton(btn_text, callback_data=callback))
        keyboard.append(btn_row)

    return InlineKeyboardMarkup(keyboard)
