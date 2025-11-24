"""
modules/quiz_game.py
MULTI-CATEGORY QUIZ GAME
Categories:
• Gaming
• Content Creation
• Crypto
• Stock Market
• Meme Coins
"""

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_user, load_db, save_db
from ui.components import render_text


XP_CORRECT = 120
XP_WRONG = 15


# ---------------------------------------------------------
# MASTER QUESTION BANK
# ---------------------------------------------------------

QUESTIONS = {
    "gaming": [
        ("What does FPS stand for?", ["First Power System", "Frames Per Second", "Final Player Score"], "Frames Per Second"),
        ("Who created PlayStation?", ["Nintendo", "Sony", "Sega"], "Sony"),
        ("Main objective in Fortnite?", ["Solve puzzles", "Build cities", "Be the last player standing"], "Be the last player standing"),
        ("Minecraft default male character?", ["Steve", "John", "Alex"], "Steve"),
        ("Which game started battle royale?", ["PUBG", "Halo", "Overwatch"], "PUBG"),
        ("First console with motion controls?", ["PS3", "Xbox 360", "Nintendo Wii"], "Nintendo Wii"),
        ("Master Chief is from?", ["Halo", "Destiny", "Mass Effect"], "Halo"),
        ("Link is from?", ["Final Fantasy", "The Legend of Zelda", "Dragon Quest"], "The Legend of Zelda"),
        ("Who created GTA?", ["Rockstar", "Activision", "Ubisoft"], "Rockstar"),
        ("Healer class type?", ["Support", "Tank", "DPS"], "Support"),
        ("Mario's brother?", ["Yoshi", "Luigi", "Wario"], "Luigi"),
        ("Genre of Call of Duty?", ["RPG", "Shooter", "Strategy"], "Shooter")
    ],

    "content": [
        ("CTR stands for…", ["Click Through Rate", "Content Tracking Ratio", "Creative Transfer Rate"], "Click Through Rate"),
        ("Platform with Shorts?", ["YouTube", "Twitch", "TikTok"], "YouTube"),
        ("Thumbnail is…", ["Video intro", "Video preview image", "Audio enhancement"], "Video preview image"),
        ("VOD stands for…", ["Viewer On Demand", "Video On Demand", "Voice Over Desk"], "Video On Demand"),
        ("Main live streaming platform?", ["Twitch", "Snapchat", "Instagram"], "Twitch"),
        ("High audience retention means…", ["People skip", "People leave early", "People watch longer"], "People watch longer"),
        ("Editing software?", ["Firefox", "Premiere Pro", "Steam"], "Premiere Pro"),
        ("Suddenly many views is called…", ["Viral", "Stagnant", "Archived"], "Viral"),
        ("Call to action is…", ["Asking viewers to do something", "Adding music", "Copyright checking"], "Asking viewers to do something"),
        ("Platform with 'duet'?", ["Instagram", "TikTok", "Facebook"], "TikTok"),
        ("A niche is…", ["Editing style", "Content topic", "Thumbnail colors"], "Content topic"),
        ("Common video format?", [".TXT", ".MP4", ".DOCX"], ".MP4"),
    ],

    "crypto": [
        ("Bitcoin is known as…", ["Digital gold", "Digital oil", "Digital silver"], "Digital gold"),
        ("HODL means…", ["Sell fast", "Hold long-term", "Borrow coins"], "Hold long-term"),
        ("Ethereum token is…", ["ETH", "ETC", "ETP"], "ETH"),
        ("Blockchain is…", ["A console", "A data ledger", "A crypto exchange"], "A data ledger"),
        ("Smart contracts are from…", ["Dogecoin", "Ethereum", "Litecoin"], "Ethereum"),
        ("DeFi means…", ["Decentralized Finance", "Default File", "Digital Funding"], "Decentralized Finance"),
        ("Meme coin?", ["Cardano", "Solana", "Dogecoin"], "Dogecoin"),
        ("Crypto exchange is…", ["Hardware wallet", "Trading platform", "File-sharing app"], "Trading platform"),
        ("Verifying blockchain transactions?", ["Mining", "Painting", "Hosting"], "Mining"),
        ("Whale means…", ["Big blockchain", "Large holder", "Type of node"], "Large holder"),
        ("NFT stands for…", ["Non-Fungible Token", "New Finance Token", "Network Fund Transfer"], "Non-Fungible Token"),
        ("Low-fee chain?", ["Solana", "Bitcoin", "Ethereum"], "Solana"),
    ],

    "stocks": [
        ("IPO stands for…", ["Initial Profit Offering", "Initial Public Offering", "Investor Portfolio Option"], "Initial Public Offering"),
        ("Bull market means…", ["Prices fall", "Prices rise", "Prices freeze"], "Prices rise"),
        ("500 top U.S. companies index?", ["S&P 500", "Dow 10", "Nasdaq 5"], "S&P 500"),
        ("Tech-heavy index?", ["FTSE", "NASDAQ", "Nikkei"], "NASDAQ"),
        ("Dividend is…", ["Company fee", "Payment to shareholders", "Tax"], "Payment to shareholders"),
        ("Bear market means…", ["Rising", "High volume", "Falling prices"], "Falling prices"),
        ("Stockbroker is…", ["Regulator", "Trader executing orders", "Loan provider"], "Trader executing orders"),
        ("Market cap is…", ["Fee", "Company valuation", "Program"], "Company valuation"),
        ("Blue-chip stock?", ["High risk", "Penny stock", "Major reliable company"], "Major reliable company"),
        ("Part of FAANG?", ["Ford", "Apple", "Airbnb"], "Apple"),
        ("Limit order means…", ["Buy any price", "Buy chosen price", "Buy after close"], "Buy chosen price"),
        ("Portfolio is…", ["Exchange", "Investments collection", "Trading app"], "Investments collection"),
    ],

    "meme": [
        ("Shiba Inu dog logo?", ["Pepe", "Dogecoin", "Floki"], "Dogecoin"),
        ("SHIB launched on…", ["Ethereum", "Solana", "Avalanche"], "Ethereum"),
        ("Meme coins are known for…", ["Utility", "Community hype", "Government backing"], "Community hype"),
        ("Frog-themed coin?", ["Pepe", "Shiba Inu", "Dogecoin"], "Pepe"),
        ("Dogecoin was created as…", ["Payment system", "A joke", "NFT launcher"], "A joke"),
        ("Associated with Elon Musk?", ["XRP", "Dogecoin", "Cardano"], "Dogecoin"),
        ("Floki Inu named after…", ["Cartoon", "Elon Musk's dog", "Investor"], "Elon Musk's dog"),
        ("Meme coins are usually…", ["Stable", "High-risk", "Government bonds"], "High-risk"),
        ("2023 viral meme coin?", ["LUNA", "PEPE", "BCH"], "PEPE"),
        ("Meme coins rely on…", ["Community", "Patents", "Gov funding"], "Community"),
        ("Low price token?", ["SHIB", "BTC", "ETH"], "SHIB"),
        ("Common meme coin risk?", ["Guaranteed profits", "Extreme volatility", "Fixed ROI"], "Extreme volatility"),
    ]
}


# ---------------------------------------------------------
# MAIN CALLBACK HANDLER
# ---------------------------------------------------------
def handle_quiz_callback(bot, update):
    q = update.callback_query
    data = q.data

    # Category selection
    if data == "quiz_menu":
        return quiz_menu(bot, update)

    # Start category
    if data.startswith("quiz_start_"):
        _, _, category = data.split("_")
        return send_question(bot, update, category)

    # Answer chosen
    if data.startswith("quiz_answer_"):
        _, _, choice, correct, category = data.split("_")
        return check_answer(bot, update, choice, correct, category)


# ---------------------------------------------------------
# QUIZ MENU
# ---------------------------------------------------------
def quiz_menu(bot, update):
    q = update.callback_query
    user = get_user(q.from_user.id)

    text = render_text(user, "🧠 *QUIZ TIME!* Choose a category:")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Gaming", callback_data="quiz_start_gaming")],
        [InlineKeyboardButton("🎥 Content Creating", callback_data="quiz_start_content")],
        [InlineKeyboardButton("🪙 Crypto", callback_data="quiz_start_crypto")],
        [InlineKeyboardButton("📈 Stock Market", callback_data="quiz_start_stocks")],
        [InlineKeyboardButton("🐕 Meme Coins", callback_data="quiz_start_meme")],
        [InlineKeyboardButton("↩️ Back", callback_data="games_main")]
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# SEND QUESTION
# ---------------------------------------------------------
def send_question(bot, update, category):
    q = update.callback_query
    user = get_user(q.from_user.id)

    question, options, correct = random.choice(QUESTIONS[category])

    text = render_text(user, f"🧠 *{category.upper()} QUIZ*\n\n{question}")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(opt, callback_data=f"quiz_answer_{opt}_{correct}_{category}")]
        for opt in options
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)


# ---------------------------------------------------------
# CHECK ANSWER
# ---------------------------------------------------------
def check_answer(bot, update, choice, correct, category):
    q = update.callback_query
    user_id = q.from_user.id
    user = get_user(user_id)

    db = load_db()
    uid = str(user_id)

    if choice == correct:
        db[uid]["xp"] += XP_CORRECT
        save_db(db)

        text = render_text(user,
            f"✅ *Correct!*\n+{XP_CORRECT} XP\n\n"
            "Next question?"
        )
    else:
        db[uid]["xp"] = max(0, db[uid]["xp"] - XP_WRONG)
        save_db(db)

        text = render_text(user,
            f"❌ *Wrong!* Correct answer: {correct}\n"
            f"Penalty: −{XP_WRONG} XP\n\nTry another?"
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Next", callback_data=f"quiz_start_{category}")],
        [InlineKeyboardButton("🎮 Games", callback_data="games_main")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu_main")]
    ])

    q.edit_message_text(text=text, parse_mode="Markdown", reply_markup=keyboard)
