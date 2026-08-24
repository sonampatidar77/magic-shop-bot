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

# Stores groups where Magic Shop has been activated
active_chats = set()

# Stores biases while the bot is running
biases = {}

# Prevents the hourly message from being sent twice
last_hour_sent = {}


# ═══════════════════════════════════════
# 𐙚 MAGIC SHOP HOURLY MESSAGE
# ═══════════════════════════════════════

HOURLY_MESSAGE = """𐙚 𝑯𝒆𝒚, 𝑩𝒖𝒏𝒏𝒊𝒆𝒔!

𝑯𝒐𝒑𝒆 𝒚𝒐𝒖’𝒓𝒆 𝒆𝒏𝒋𝒐𝒚𝒊𝒏𝒈 𝒚𝒐𝒖𝒓 𝒔𝒕𝒂𝒚 𝒂𝒕 𝑴𝒂𝒈𝒊𝒄 𝑺𝒉𝒐𝒑, surrounded by all the amazing people here 🤍

✦ 𝑨 𝒍𝒊𝒕𝒕𝒍𝒆 𝒓𝒆𝒎𝒊𝒏𝒅𝒆𝒓:
Please make sure you’re following the rules and treating everyone with kindness ♡
𝑫𝒐𝒏’𝒕 𝒊𝒈𝒏𝒐𝒓𝒆 𝒂𝒏𝒚𝒐𝒏𝒆 — everyone deserves to feel included here.

If you ever feel ignored, uncomfortable, or face any issue, 𝒇𝒆𝒆𝒍 𝒇𝒓𝒆𝒆 𝒕𝒐 𝒕𝒂𝒈 𝒂𝒏𝒚 𝒂𝒅𝒎𝒊𝒏 or simply use @admin. We’re always here to help.

𓂃 ࣪˖ 𝑻𝒉𝒂𝒏𝒌 𝒚𝒐𝒖 for being a part of our little shop!
𝑯𝒂𝒗𝒆 𝒂 𝒈𝒐𝒐𝒅 𝒕𝒊𝒎𝒆 ♡

𝑩𝒐𝒓𝒂𝒉𝒂𝒆 💜"""


# ═══════════════════════════════════════
# 𐙚 BASIC
# ═══════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if update.effective_chat.type != "private":
        active_chats.add(chat_id)

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
    await update.message.reply_text(
        """𐙚 𝑴𝒂𝒈𝒊𝒄 𝑺𝒉𝒐𝒑 𝑴𝒆𝒏𝒖

💜 𝑨𝑹𝑴𝒀
/vibecheck
/bias
/stream
/borahae
/btsquiz
/era

✦ 𝑪𝒉𝒂𝒐𝒔
/do_nothing
/roast
/hug
/slap
/yeet
/poll
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
    )


# ═══════════════════════════════════════
# 💜 ARMY
# ═══════════════════════════════════════

async def vibecheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    levels = [
        "Casual Listener ♡",
        "ARMY in Training ✦",
        "Certified ARMY 💜",
        "Full Borahae Energy ♡",
        "Maximum ARMY Chaos ✦",
    ]

    await update.message.reply_text(
        f"𐙚 𝑽𝒊𝒃𝒆 𝑪𝒉𝒆𝒄𝒌\n\n"
        f"{random.choice(levels)}"
    )


async def bias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.args:
        chosen = " ".join(context.args)
        biases[user_id] = chosen

        await update.message.reply_text(
            f"𐙚 𝑩𝒊𝒂𝒔 𝒔𝒂𝒗𝒆𝒅 ♡\n\n"
            f"Your bias: {chosen}"
        )
    elif user_id in biases:
        await update.message.reply_text(
            f"𐙚 𝒀𝒐𝒖𝒓 𝒃𝒊𝒂𝒔 ♡\n\n"
            f"{biases[user_id]}"
        )
    else:
        await update.message.reply_text(
            "𐙚 𝑾𝒉𝒐'𝒔 𝒚𝒐𝒖𝒓 𝒃𝒊𝒂𝒔?\n\n"
            "Use /bias followed by a name to save it ♡"
        )


async def stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "𐙚 𝑺𝒕𝒓𝒆𝒂𝒎 𝒄𝒉𝒆𝒄𝒌 ♡\n\n"
        "Your group's streaming message/link can be added here."
    )


async def borahae(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "𐙚 𝑨 𝒍𝒊𝒕𝒕𝒍𝒆 𝑩𝒐𝒓𝒂𝒉𝒂𝒆 𝒇𝒐𝒓 𝒆𝒗𝒆𝒓𝒚𝒐𝒏𝒆 💜"
    )


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
        ("Which BTS album includes Spring Day?", "You Never Walk Alone"),
    ]

    question, answer = random.choice(quizzes)

    await update.message.reply_text(
        f"💜 𝑩𝑻𝑺 𝑸𝒖𝒊𝒛\n\n"
        f"{question}\n\n"
        f"Answer: {answer}"
    )


# ═══════════════════════════════════════
# ✦ CHAOS
# ═══════════════════════════════════════

async def do_nothing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "𐙚 𝑴𝒂𝒈𝒊𝒄 𝑺𝒉𝒐𝒑 is doing absolutely nothing right now ♡\n\n"
        "Please come back later."
    )


async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "everyone"

    await update.message.reply_text(
        f"𐙚 sending a little hug to {target} ♡"
    )


async def roast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "you"

    roasts = [
        "you really thought that was a good idea 😭",
        "respectfully... what are you doing ♡",
        "even Magic Shop needs a moment after that one.",
        "your chaos is truly unmatched.",
        "I have no words. And that's saying something.",
    ]

    await update.message.reply_text(
        f"𐙚 {target}, {random.choice(roasts)}"
    )


async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "you"

    await update.message.reply_text(
        f"𐙚 *dramatically bonks {target} with a pillow* ♡"
    )


async def yeet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "someone"

    await update.message.reply_text(
        f"𐙚 {target} has been dramatically yeeted into the "
        "fictional void ♡"
    )


async def fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fortunes = [
        "Something nice may find its way to you today ♡",
        "A good surprise is waiting somewhere nearby ✦",
        "Today might be better than you expect.",
        "Your luck is looking pretty good today ♡",
        "Take a little break. You deserve it.",
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


async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "𐙚 Use it like:\n\n"
            "/poll What's your favourite BTS era?"
        )
        return

    question = " ".join(context.args)

    await update.message.reply_poll(
        question=question,
        options=["Yes ♡", "No", "Maybe", "I don't know"]
    )


# ═══════════════════════════════════════
# 🎮 GAMES
# ═══════════════════════════════════════

async def wordgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    words = [
        "ARMY",
        "BORAHАE",
        "PURPLE",
        "MAGIC",
        "PETAL",
        "BTS",
        "DYNAMITE",
        "WINGS",
    ]

    word = random.choice(words)
    scrambled = "".join(random.sample(word, len(word)))

    await update.message.reply_text(
        f"𐙚 𝑾𝒐𝒓𝒅 𝑮𝒂𝒎𝒆\n\n"
        f"Unscramble this:\n\n"
        f"**{scrambled}**\n\n"
        f"What's the word?"
    )


async def duo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = " ".join(context.args) if context.args else "someone"

    games = [
        "Rock Paper Scissors",
        "Word Battle",
        "Trivia",
        "Coin Flip",
    ]

    await update.message.reply_text(
        f"𐙚 {target}, you've been challenged to "
        f"{random.choice(games)} ♡"
    )


async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = random.choice([
        "🪨 Rock",
        "📄 Paper",
        "✂️ Scissors"
    ])

    await update.message.reply_text(
        f"𐙚 Magic Shop chose: {choice}"
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
        "your presence is always appreciated ♡",
        "you have such a lovely energy.",
        "you're doing better than you think ✦",
        "Magic Shop approves of you ♡",
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
        "𐙚 𝑺𝒉𝒖𝒔𝒉 mode activated ♡\n\n"
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

    # Only send at the beginning of each hour
    if now.minute != 0:
        return

    current_hour = now.strftime("%Y-%m-%d-%H")

    for chat_id in list(active_chats):

        # Prevent duplicate messages during the same hour
        if last_hour_sent.get(chat_id) == current_hour:
            continue

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=HOURLY_MESSAGE
            )

            last_hour_sent[chat_id] = current_hour

        except Exception:
            pass


# ═══════════════════════════════════════
# 🪄 START MAGIC SHOP
# ═══════════════════════════════════════
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Magic Shop Bot is running!")

    def log_message(self, format, *args):
        pass


def start_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()
    
def main():

    threading.Thread(target=start_web_server, daemon=True).start()

    if not TOKEN:

        raise RuntimeError(
            "BOT_TOKEN is missing. Add it privately in your hosting settings."
        )

    app = Application.builder().token(TOKEN).build()

    # Basic
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # ARMY
    app.add_handler(CommandHandler("vibecheck", vibecheck))
    app.add_handler(CommandHandler("bias", bias))
    app.add_handler(CommandHandler("stream", stream))
    app.add_handler(CommandHandler("borahae", borahae))
    app.add_handler(CommandHandler("btsquiz", btsquiz))
    app.add_handler(CommandHandler("era", era))

    # Chaos
    app.add_handler(CommandHandler("do_nothing", do_nothing))
    app.add_handler(CommandHandler("roast", roast))
    app.add_handler(CommandHandler("hug", hug))
    app.add_handler(CommandHandler("slap", slap))
    app.add_handler(CommandHandler("yeet", yeet))
    app.add_handler(CommandHandler("poll", poll))
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

    # Check every minute for the hourly message
    if app.job_queue:
        app.job_queue.run_repeating(
            hourly_check,
            interval=60,
            first=10
        )

    print("𐙚 Magic Shop is running ♡")

    app.run_polling()


if __name__ == "__main__":
    main()
