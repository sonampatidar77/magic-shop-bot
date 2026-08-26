import os
import random
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.environ.get("BOT_TOKEN")

# ═══════════════════════════════════════
# 𐙚 MAGIC SHOP DATA
# ═══════════════════════════════════════

active_chats = set()
biases = {}
last_hour_sent = {}

# ═══════════════════════════════════════
# 𐙚 HOURLY MESSAGE — KEEPING YOUR EXACT TEXT
# ═══════════════════════════════════════

HOURLY_MESSAGE = """‎ꫂ𝑯𝘦𝘺 𝑻𝘩𝘦𝘳𝘦  𝑴𝘰𝘰𝘯𝘪𝘦𝘴 𓍼

𝘩𝘰𝘱𝘦 𝘶𝘳 𝘩𝘢𝘷𝘪𝘯𝘨 𝘢 𝘯𝘪𝘤𝘦 𝘵𝘪𝘮𝘦 𝘢𝘵 𝘔𝘢𝘨𝘪𝘤 𝘚𝘩𝘰𝘱 𝘴𝘰 𝘧𝘢𝘳 
𝘥𝘰𝘯’𝘵 𝘩𝘦𝘴𝘪𝘵𝘢𝘵𝘦 𝘵𝘰 𝘫𝘰𝘪𝘯 𝘵𝘩𝘦 𝘤𝘰𝘯𝘷𝘦𝘳𝘴𝘢𝘵𝘪𝘰𝘯𝘴, 𝘮𝘢𝘬𝘦 𝘴𝘰𝘮𝘦 𝘯𝘦𝘸 𝘧𝘳𝘪𝘦𝘯𝘥𝘴 & 𝘴𝘱𝘳𝘦𝘢𝘥 𝘢 𝘭𝘪𝘵𝘵𝘭𝘦 𝘬𝘪𝘯𝘥𝘯𝘦𝘴𝘴 𝘢𝘳𝘰𝘶𝘯𝘥 <3
𝘪𝘧 𝘺𝘰𝘶 𝘦𝘷𝘦𝘳 𝘧𝘦𝘦𝘭 𝘭𝘦𝘧𝘵 𝘰𝘶𝘵 𝘰𝘳 𝘩𝘢𝘷𝘦 𝘢𝘯𝘺 𝘪𝘴𝘴𝘶𝘦, 𝘧𝘦𝘦𝘭 𝘧𝘳𝘦𝘦 𝘵𝘰 𝘵𝘢𝘨 @𝘢𝘥𝘮𝘪𝘯 — 𝘸𝘦’𝘳𝘦 𝘢𝘭𝘸𝘢𝘺𝘴 𝘩𝘦𝘳𝘦 𝘵𝘰 𝘩𝘦𝘭𝘱.𝘯𝘰 𝘪𝘴𝘴𝘶𝘦 𝘪𝘴 𝘵𝘰𝘰 𝘴𝘮𝘢𝘭𝘭 𝘵𝘰 𝘮𝘦𝘯𝘵𝘪𝘰𝘯 
𝘮𝘢𝘬𝘦 𝘴𝘶𝘳𝘦 𝘵𝘰 𝘧𝘰𝘭𝘭𝘰𝘸 𝘵𝘩𝘦 𝘳𝘶𝘭𝘦𝘴 𝘏𝘢𝘷𝘦 𝘢 𝘭𝘰𝘷𝘦𝘭𝘺 𝘵𝘪𝘮𝘦 𝘩𝘦𝘳𝘦 
𝘣𝘰𝘳𝘢𝘩𝘢𝘦 💜"""

# ═══════════════════════════════════════
# 𐙚 NEW MEMBER WELCOME — YOUR EXACT TEXT
# ═══════════════════════════════════════

WELCOME_MESSAGE = """𐙚 {mention}, annyeong! 🪄

welcome to 𝐌𝐚𝐠𝐢𝐜 𝐒𝐡𝐨𝐩 
we’re glad to have you here 

★ 𝐒𝐭𝐚𝐲 𝐮𝐩𝐝𝐚𝐭𝐞𝐝
join our channel → @wingsofecho

make yourself comfortable & have a lovely time here 
borahae 💜"""

# ═══════════════════════════════════════
# 𐙚 HELP
# ═══════════════════════════════════════

HELP_MESSAGE = """𐙚 𝑴𝒂𝒈𝒊𝒄 𝑺𝒉𝒐𝒑 𝑴𝒆𝒏𝒖

💜 𝑨𝑹𝑴𝒀
/vibecheck
/bias
/borahae
/btsquiz
/era

✦ 𝑪𝒉𝒂𝒐𝒔
/do_nothing
/roast
/hug
/slap
/yeet
/ship
/fortune

🎮 𝑮𝒂𝒎𝒆𝒔
/wordgame
/duo
/rps
/coinflip
/dice
/8ball
/trivia

♡ 𝑺𝒐𝒄𝒊𝒂𝒍
/compliment
/match
/truth
/dare
/wouldyourather
/question

🛡️ 𝑨𝒅𝒎𝒊𝒏
/shush
/unyeet
/warn
/warnings
/rules"""

# ═══════════════════════════════════════
# 𐙚 BASIC
# ═══════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type != "private":
        active_chats.add(chat.id)
        await update.message.reply_text(
            "𐙚 𝑴𝒂𝒈𝒊𝒄 𝑺𝒉𝒐𝒑 is here ♡\n\n"
            "Hourly messages are now activated for this group.\n"
            "Use /help to see what I can do."
        )
    else:
        await update.message.reply_text(
            "𐙚 𝑯𝒆𝒍𝒍𝒐 ♡\n\n"
            "I'm the little Magic Shop bot.\n"
            "Add me to your group and use /start there to activate me."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MESSAGE)


async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for member in update.message.new_chat_members:
        if member.is_bot:
            continue

        mention = member.mention_html()
        await update.message.reply_html(
            WELCOME_MESSAGE.format(mention=mention)
        )

# ═══════════════════════════════════════
# 💜 ARMY
# ═══════════════════════════════════════

async def vibecheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    levels = [
        "casual listener ♡",
        "𝑨𝑹𝑴𝒀 in training ✦",
        "Certified ARMY 💜",
        "full borahae energy",
        "maximum BTS chaos 😭",
        "one playlist away from losing it",
    ]
    await update.message.reply_text(
        f"𐙚 𝑽𝒊𝒃𝒆 𝑪𝒉𝒆𝒄𝒌\n\n{random.choice(levels)}"
    )


async def bias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.args:
        chosen = " ".join(context.args)
        biases[user_id] = chosen
        await update.message.reply_text(
            f"𐙚 𝑩𝒊𝒂𝒔 𝒔𝒂𝒗𝒆𝒅 ♡\n\nYour bias: {chosen}"
        )
    elif user_id in biases:
        await update.message.reply_text(
            f"𐙚 𝒀𝒐𝒖𝒓 𝒃𝒊𝒂𝒔 ♡\n\n{biases[user_id]}"
        )
    else:
        await update.message.reply_text(
            "𐙚 𝑾𝒉𝒐'𝒔 𝒚𝒐𝒖𝒓 𝒃𝒊𝒂𝒔?\n\n"
            "Use /bias followed by a name to save it ♡"
        )


async def borahae(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = [
        "𐙚 a little borahae for the timeline 💜",
        "borahae. that's it. that's the command. 💜",
        "𐙚 purple hearts have entered the chat.",
        "𝑩𝒐𝒓𝒂𝒉𝒂𝒆 💜 now go bother your favourite person.",
    ]
    await update.message.reply_text(random.choice(messages))


async def era(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eras = [
        "HYYH era 🌸",
        "Wings era 🪽",
        "Love Yourself era ♡",
        "MOTS era ✦",
        "BE era ☁️",
        "Proof era 💜",
        "Arirang era 🌷",
    ]
    await update.message.reply_text(
        f"𐙚 𝒀𝒐𝒖𝒓 𝒓𝒂𝒏𝒅𝒐𝒎 𝑩𝑻𝑺 𝒆𝒓𝒂:\n\n"
        f"{random.choice(eras)}"
    )


async def btsquiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quizzes = [
        ("How many members are in BTS?", "7"),
        ("What is BTS's fandom called?", "ARMY"),
        ("What does BTS stand for in English?", "Beyond the Scene"),
        ("Which album includes Spring Day?", "You Never Walk Alone"),
        ("Which BTS song became their first Billboard Hot 100 #1?", "Dynamite"),
    ]
    question, answer = random.choice(quizzes)
    await update.message.reply_text(
        f"💜 𝑩𝑻𝑺 𝑸𝒖𝒊𝒛\n\n{question}\n\n"
        f"Answer: {answer}"
    )

# ═══════════════════════════════════════
# ✦ CHAOS
# ═══════════════════════════════════════

async def do_nothing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "𐙚 𝑴𝒂𝒈𝒊𝒄 𝑺𝒉𝒐𝒑 is currently doing absolutely nothing.\n\n"
        "finally, a productive day."
    )


async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "everyone"
    await update.message.reply_text(
        f"𐙚 sending {target} a very normal, non-dramatic hug ♡"
    )


async def roast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "you"

    roasts = [
        "you have the confidence of someone who did not read the instructions 😭",
        "respectfully, even autocorrect gave up on you.",
        "I've seen loading screens with more personality.",
        "you really woke up and chose to be someone's headache.",
        "that was certainly a decision. not a good one, but a decision.",
        "your brain said 'we ball' and immediately left.",
        "I would roast you harder but I don't want to overwork the bot.",
        "you're proof that Wi-Fi isn't the only thing that needs reconnecting.",
        "the confidence? impressive. the logic? missing.",
        "10/10 commitment to being slightly inconvenient.",
        "bro is fighting battles nobody assigned 😭",
        "I could say something devastating but honestly... you're already doing enough.",
        "even the group chat needs a moment to process you.",
        "that comeback arrived three business days late.",
        "you bring a unique energy. unfortunately, it is mostly confusion.",
    ]

    await update.message.reply_text(
        f"𐙚 {target}, {random.choice(roasts)}"
    )


async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "you"
    await update.message.reply_text(
        f"𐙚 *gently bonks {target} with a pillow* ♡"
    )


async def yeet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "someone"
    await update.message.reply_text(
        f"𐙚 {target} has been dramatically yeeted into the "
        "fictional void ♡"
    )


async def fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fortunes = [
        "something nice may find its way to you today ♡",
        "a good surprise is waiting somewhere nearby ✦",
        "today might be better than you expect.",
        "your luck is looking suspiciously decent today.",
        "take a little break. you deserve it.",
        "someone is probably thinking about you. don't ask me who 😭",
    ]
    await update.message.reply_text(
        f"✦ 𝑭𝒐𝒓𝒕𝒖𝒏𝒆\n\n{random.choice(fortunes)}"
    )


async def ship(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) >= 2:
        first = context.args[0]
        second = context.args[1]
    else:
        first = "you"
        second = "someone"

    score = random.randint(1, 100)
    await update.message.reply_text(
        f"𐙚 𝑴𝒂𝒈𝒊𝒄 𝑺𝒉𝒐𝒑 𝑴𝒂𝒕𝒄𝒉\n\n"
        f"{first} × {second}\n"
        f"Compatibility: {score}% ♡"
    )

# ═══════════════════════════════════════
# 🎮 GAMES
# ═══════════════════════════════════════

async def wordgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words = [
        "ARMY", "BORAHАE", "PURPLE", "MAGIC",
        "PETAL", "BTS", "DYNAMITE", "WINGS",
    ]
    word = random.choice(words)
    scrambled = "".join(random.sample(word, len(word)))

    await update.message.reply_text(
        f"𐙚 𝑾𝒐𝒓𝒅 𝑮𝒂𝒎𝒆\n\n"
        f"Unscramble this:\n\n"
        f"{scrambled}\n\n"
        f"What's the word?"
    )


async def duo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "the two of you"

    lines = [
        f"𐙚 𝑩𝒆𝒔𝒕 𝑫𝒖𝒐 𝑪𝒉𝒆𝒄𝒌\n\n{target}\n"
        "the kind of duo that turns one bad idea into a group project 😭",
        f"𐙚 {target}\n"
        "elite duo energy. absolutely no romance department involved. ♡",
        f"𐙚 𝑫𝒖𝒐 𝑹𝒂𝒕𝒊𝒏𝒈\n\n{target}\n"
        f"{random.randint(70, 100)}% certified menace duo.",
        f"𐙚 {target} are giving\n"
        "one shared brain cell, excellent teamwork.",
        f"𐙚 bestie duo detected.\n"
        f"{target} should probably not be left unsupervised.",
    ]
    await update.message.reply_text(random.choice(lines))


async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = random.choice(["🪨 Rock", "📄 Paper", "✂️ Scissors"])
    await update.message.reply_text(
        f"𐙚 Magic Shop chose: {choice}\n"
        "your turn. don't embarrass yourself."
    )


async def coinflip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"𐙚 The coin says: {random.choice(['Heads ♡', 'Tails ✦'])}"
    )


async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🎲 You rolled a {random.randint(1, 6)}"
    )


async def eightball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answers = [
        "Yes ♡",
        "Probably.",
        "Maybe ✦",
        "Ask again later.",
        "The signs say yes.",
        "The signs say no.",
        "Magic Shop isn't sure 😭",
        "absolutely not. next question.",
    ]
    await update.message.reply_text(
        f"𐙚 𝟖-𝑩𝒂𝒍𝒍\n\n{random.choice(answers)}"
    )


async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    facts = [
        "Honey doesn't spoil easily. 🍯",
        "Octopuses have three hearts. 🐙",
        "A group of flamingos is called a flamboyance. 🦩",
        "Bananas are botanically berries. 🍌",
        "The Eiffel Tower can change height slightly with temperature. 🗼",
    ]
    await update.message.reply_text(
        f"✦ 𝑻𝒓𝒊𝒗𝒊𝒂\n\n{random.choice(facts)}"
    )

# ═══════════════════════════════════════
# ♡ SOCIAL
# ═══════════════════════════════════════

async def compliment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "you"
    compliments = [
        "you make this place a little nicer just by being here 🤍",
        "your presence is actually appreciated, don't let it get to your head ♡",
        "you have a pretty lovely energy.",
        "you're doing better than you think ✦",
        "Magic Shop approves of you. temporarily.",
    ]
    await update.message.reply_text(
        f"𐙚 {target}, {random.choice(compliments)}"
    )


async def match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "someone"
    score = random.randint(1, 100)
    await update.message.reply_text(
        f"𐙚 𝑴𝒂𝒕𝒄𝒉 𝑴𝒆𝒕𝒆𝒓\n\n"
        f"You × {target}\n"
        f"Friendship compatibility: {score}% ♡"
    )


async def truth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        "What's your current favourite song?",
        "Who was your first BTS bias?",
        "What's something you're currently obsessed with?",
        "What's one thing that always makes you happy?",
        "What's a song you know every word to?",
    ]
    await update.message.reply_text(
        f"𐙚 𝑻𝒓𝒖𝒕𝒉\n\n{random.choice(questions)}"
    )


async def dare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dares = [
        "Send the last emoji you used.",
        "Compliment someone in the group.",
        "Send a random GIF.",
        "Describe your mood using only emojis.",
        "Say Borahae in the chat. 💜",
    ]
    await update.message.reply_text(
        f"✦ 𝑫𝒂𝒓𝒆\n\n{random.choice(dares)}"
    )


async def wouldyourather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        "Would you rather meet BTS or get unlimited concert tickets?",
        "Would you rather have unlimited snacks or unlimited music?",
        "Would you rather always be early or always be late?",
        "Would you rather travel everywhere or stay home forever?",
    ]
    await update.message.reply_text(
        f"𐙚 𝑾𝒐𝒖𝒍𝒅 𝒀𝒐𝒖 𝑹𝒂𝒕𝒉𝒆𝒓\n\n"
        f"{random.choice(questions)}"
    )


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        "What's one song you could listen to forever?",
        "What's your favourite BTS era?",
        "What's your comfort movie?",
        "If you could travel anywhere tomorrow, where would you go?",
        "What's something that instantly makes you happy?",
    ]
    await update.message.reply_text(
        f"✦ 𝑸𝒖𝒆𝒔𝒕𝒊𝒐𝒏 𝒐𝒇 𝒕𝒉𝒆 𝒎𝒐𝒎𝒆𝒏𝒕\n\n"
        f"{random.choice(questions)}"
    )

# ═══════════════════════════════════════
# 🛡️ ADMIN
# ═══════════════════════════════════════

async def check_admin(update: Update):
    member = await update.effective_chat.get_member(
        update.effective_user.id
    )
    return member.status in ["administrator", "creator"]


async def shush(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update):
        await update.message.reply_text(
            "𐙚 This command is for admins only ♡"
        )
        return

    await update.message.reply_text(
        "𐙚 𝑺𝒉𝒖𝒔𝒉 mode request received ♡\n\n"
        "Reply to a member's message when using this command "
        "to mute them."
    )


async def unyeet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update):
        await update.message.reply_text(
            "𐙚 This command is for admins only ♡"
        )
        return

    await update.message.reply_text(
        "𐙚 𝑼𝒏𝒚𝒆𝒕 request received ♡"
    )


async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update):
        await update.message.reply_text(
            "𐙚 This command is for admins only ♡"
        )
        return

    await update.message.reply_text(
        "𐙚 𝑾𝒂𝒓𝒏𝒊𝒏𝒈 issued ♡"
    )


async def warnings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "𐙚 𝑾𝒂𝒓𝒏𝒊𝒏𝒈𝒔\n\n"
        "No saved warnings yet ♡"
    )


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """𐙚 𝑴𝒂𝒈𝒊𝒄 𝑺𝒉𝒐𝒑 𝑹𝒖𝒍𝒆𝒔

♡ Please be respectful to everyone.
♡ Don't ignore or purposely exclude members.
♡ No unnecessary drama or spam.
♡ Follow the admins' instructions.
♡ Keep the group comfortable and welcoming.

If you're ever uncomfortable or have an issue,
please reach out to an admin.

𝑩𝒐𝒓𝒂𝒉𝒂𝒆 💜"""
    )

# ═══════════════════════════════════════
# ⏰ HOURLY SYSTEM
# ═══════════════════════════════════════

async def hourly_check(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    if now.minute != 0:
        return

    current_hour = now.strftime("%Y-%m-%d-%H")

    for chat_id in list(active_chats):
        if last_hour_sent.get(chat_id) == current_hour:
            continue

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=HOURLY_MESSAGE,
            )
            last_hour_sent[chat_id] = current_hour
        except Exception as exc:
            print(f"Hourly message failed for {chat_id}: {exc}")

# ═══════════════════════════════════════
# 🌐 RENDER HEALTH SERVER
# ═══════════════════════════════════════

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Magic Shop Bot is running!")

    def log_message(self, format, *args):
        pass


def start_web_server():
    port = int(os.environ.get("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health server running on port {port}")
    server.serve_forever()

# ═══════════════════════════════════════
# 🪄 START MAGIC SHOP
# ═══════════════════════════════════════

def main():
    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is missing. Add it privately in your Render "
            "Environment Variables."
        )

    threading.Thread(
        target=start_web_server,
        daemon=True,
    ).start()

    app = Application.builder().token(TOKEN).build()

    # Basic
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # New members
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            new_member,
        )
    )

    # ARMY
    app.add_handler(CommandHandler("vibecheck", vibecheck))
    app.add_handler(CommandHandler("bias", bias))
    app.add_handler(CommandHandler("borahae", borahae))
    app.add_handler(CommandHandler("btsquiz", btsquiz))
    app.add_handler(CommandHandler("era", era))

    # Chaos
    app.add_handler(CommandHandler("do_nothing", do_nothing))
    app.add_handler(CommandHandler("roast", roast))
    app.add_handler(CommandHandler("hug", hug))
    app.add_handler(CommandHandler("slap", slap))
    app.add_handler(CommandHandler("yeet", yeet))
    app.add_handler(CommandHandler("ship", ship))
    app.add_handler(CommandHandler("fortune", fortune))

    # Games
    app.add_handler(CommandHandler("wordgame", wordgame))
    app.add_handler(CommandHandler("duo", duo))
    app.add_handler(CommandHandler("rps", rps))
    app.add_handler(CommandHandler("coinflip", coinflip))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("8ball", eightball))
    app.add_handler(CommandHandler("trivia", trivia))

    # Social
    app.add_handler(CommandHandler("compliment", compliment))
    app.add_handler(CommandHandler("match", match))
    app.add_handler(CommandHandler("truth", truth))
    app.add_handler(CommandHandler("dare", dare))
    app.add_handler(CommandHandler("wouldyourather", wouldyourather))
    app.add_handler(CommandHandler("question", question))

    # Admin
    app.add_handler(CommandHandler("shush", shush))
    app.add_handler(CommandHandler("unyeet", unyeet))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("warnings", warnings))
    app.add_handler(CommandHandler("rules", rules))

    # Hourly message
    if app.job_queue:
        app.job_queue.run_repeating(
            hourly_check,
            interval=60,
            first=10,
        )
    else:
        print("WARNING: Job queue is unavailable.")

    print("𐙚 Magic Shop is running ♡")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
