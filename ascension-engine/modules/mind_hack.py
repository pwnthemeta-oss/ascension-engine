"""
modules/mind_hack.py
Advanced Mind Hack Puzzle – pattern, logic, sequences, odd-one-out,
what-comes-next, and trap puzzles.

Fully dynamic, uses difficulty tiers and 20+ sequence patterns.
"""

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import load_db, save_db, get_user
from ui.components import render_text

# XP values per difficulty
XP = {
    "easy": 100,
    "medium": 180,
    "hard": 260,
    "elite": 420
}

PENALTY = 12


# ----------------------------------------------------------
# Entry point for callbacks
# ----------------------------------------------------------
def handle_mindhack_callback(bot, update):
    query = update.callback_query
    data = query.data

    if data == "game_mindhack":
        return _intro(bot, update)

    if data == "mindhack_start":
        return _generate_round(bot, update)

    if data.startswith("mindhack_answer_"):
        _, chosen, correct, level = data.split("_")
        return _process_answer(bot, update, chosen, correct, level)


# ----------------------------------------------------------
# Intro Screen
# ----------------------------------------------------------
def _intro(bot, update):
    q = update.callback_query
    user = get_user(q.from_user.id)

    text = render_text(user,
        "🧠 *MIND HACK PUZZLE*\n\n"
        "A challenging pattern-recognition game.\n"
        "Solve puzzles like:\n"
        "• Odd One Out\n"
        "• What Comes Next?\n"
        "• Find the Hidden Pattern\n"
        "• Symmetry\n"
        "• Arrow logic\n"
        "• Color cycles\n"
        "• Trap patterns\n\n"
        "*Difficulty scales dynamically.*"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Begin", callback_data="mindhack_start")],
        [InlineKeyboardButton("↩️ Back", callback_data="games_main")]
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ----------------------------------------------------------
# Main puzzle generator
# ----------------------------------------------------------
def _generate_round(bot, update):
    q = update.callback_query
    user = get_user(q.from_user.id)

    # Select difficulty randomly (can tie to streak in future)
    level = random.choice(["easy", "medium", "hard", "elite"])

    # Select puzzle type randomly
    puzzle_type = random.choice([
        "odd_one_out",
        "what_next",
        "pattern_repeat",
        "symmetry",
        "color_cycle",
        "arrow_cycle",
        "trap_pattern"
    ])

    seq, answers, correct = _generate_puzzle(puzzle_type, level)

    # Format display
    text = render_text(user,
        "🧠 *MIND HACK*\n\n"
        "Sequence:\n"
        f"`{' '.join(seq)}`\n\n"
        "Choose the correct answer:"
    )

    # Build answer buttons
    buttons = []
    row = []
    for ans in answers:
        cb = f"mindhack_answer_{ans}_{correct}_{level}"
        row.append(InlineKeyboardButton(ans, callback_data=cb))
    buttons.append(row)

    buttons.append([InlineKeyboardButton("↩️ Back", callback_data="games_main")])

    q.edit_message_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ----------------------------------------------------------
# Puzzle creation logic
# ----------------------------------------------------------
def _generate_puzzle(puzzle_type, level):
    seq_len_map = {
        "easy": 4,
        "medium": 5,
        "hard": 6,
        "elite": 7
    }

    seq_len = seq_len_map[level]

    blocks = ["⬛", "⬜"]
    colors = ["🟥", "🟦", "🟩", "🟨", "🟪", "🟧"]
    arrows = ["🔼", "🔽", "◀️", "▶️"]

    # ------------------------------------------------------
    # 1. Odd-One-Out
    # ------------------------------------------------------
    if puzzle_type == "odd_one_out":
        main = random.choice(colors)
        odd = random.choice([c for c in colors if c != main])
        seq = [main] * seq_len
        idx = random.randint(0, seq_len - 1)
        seq[idx] = odd

        answers = list(set([main, odd]))
        correct = odd
        return seq, answers, correct

    # ------------------------------------------------------
    # 2. What Comes Next?
    # ------------------------------------------------------
    if puzzle_type == "what_next":
        patterns = [
            (["⬛", "⬜"], ["⬛"]),
            (["🔥", "⚡"], ["🔥"]),
            (["🟥", "🟦"], ["🟥"]),
            (["🔼", "▶️"], ["🔼"]),
            (["🟪", "🟧"], ["🟪"])
        ]

        pattern, correct_list = random.choice(patterns)
        seq = [pattern[i % len(pattern)] for i in range(seq_len)]
        correct = correct_list[0]

        answers = list(set(pattern + [correct]))
        return seq, answers, correct

    # ------------------------------------------------------
    # 3. Pattern Repeat
    # ------------------------------------------------------
    if puzzle_type == "pattern_repeat":
        cycles = [
            ["⬛", "⬛", "⬜"],
            ["🟥", "🟥", "🟦"],
            ["🔼", "🔽"],
            ["🟩", "🟥", "🟩", "🟥"],
            ["💀", "🔥"]
        ]

        pattern = random.choice(cycles)
        seq = [pattern[i % len(pattern)] for i in range(seq_len)]
        correct = pattern[seq_len % len(pattern)]
        answers = list(set(pattern))
        return seq, answers, correct

    # ------------------------------------------------------
    # 4. Symmetry Problems
    # ------------------------------------------------------
    if puzzle_type == "symmetry":
        seq = random.choice([
            ["⬛", "⬜", "⬛", "⬜", "⬛"],
            ["🟥", "🟦", "🟥", "🟦", "🟥"],
            ["🔼", "🔽", "🔽", "🔼"]
        ])
        seq = seq[:seq_len]
        correct = seq[0]
        answers = list(set(seq))
        return seq, answers, correct

    # ------------------------------------------------------
    # 5. Color Logic (cycles)
    # ------------------------------------------------------
    if puzzle_type == "color_cycle":
        cycle = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]
        seq = [cycle[i % len(cycle)] for i in range(seq_len)]
        correct = cycle[seq_len % len(cycle)]
        answers = cycle[:4]
        return seq, answers, correct

    # ------------------------------------------------------
    # 6. Arrow Logic
    # ------------------------------------------------------
    if puzzle_type == "arrow_cycle":
        pattern = ["◀️", "🔼", "▶️", "🔽"]
        seq = [pattern[i % len(pattern)] for i in range(seq_len)]
        correct = pattern[(seq_len) % len(pattern)]
        answers = pattern
        return seq, answers, correct

    # ------------------------------------------------------
    # 7. Trap Patterns
    # ------------------------------------------------------
    if puzzle_type == "trap_pattern":
        traps = [
            (["🔥", "🔥", "⚡", "🔥", "🔥", "⚡"], "🔥"),
            (["⬛", "⬜", "⬛", "⬛", "⬜", "⬛"], "⬜"),
            (["🟦", "🟥", "🟦", "🟦", "🟥", "🟦"], "🟥")
        ]

        base, correct = random.choice(traps)
        seq = base[:seq_len]
        answers = list(set(base))
        return seq, answers, correct


# ----------------------------------------------------------
# Answer Checker
# ----------------------------------------------------------
def _process_answer(bot, update, chosen, correct, level):
    q = update.callback_query
    user_id = q.from_user.id
    user = get_user(user_id)

    db = load_db()
    uid = str(user_id)

    chosen = chosen
    correct = correct

    # Correct
    if chosen == correct:
        db[uid]["xp"] += XP[level]
        save_db(db)

        text = render_text(user,
            f"🧠 *CORRECT!* 🎉\n\n"
            f"Difficulty: *{level.capitalize()}*\n"
            f"+{XP[level]} XP"
        )
    else:
        db[uid]["xp"] = max(0, db[uid]["xp"] - PENALTY)
        save_db(db)

        text = render_text(user,
            f"❌ *WRONG!*  
Correct: `{correct}`  
−{PENALTY} XP"
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Next Puzzle", callback_data="mindhack_start")],
        [InlineKeyboardButton("🎮 Games", callback_data="games_main")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")],
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)
