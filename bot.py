from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import datetime

# Bot ka token
TOKEN = "8347661235:AAHmS5A6o7sMxpVB8KXs1N8jA_g2e3-Vogg"

# Channels
CHANNEL_ID = "@shivamkmrthakur"               # ✅ Join check channel
SOURCE_CHANNEL = "@missioncatalystbotcontents"  # ✅ Source lectures channel

# Second step verification code
VERIFY_CODE = "76353736"

# Store verification expiry
verified_users = {}   # {user_id: expiry_time}


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    # Agar verification redirect se aaye
    args = context.args
    if args and args[0] == VERIFY_CODE:
        expiry = datetime.datetime.now() + datetime.timedelta(hours=24)
        verified_users[user_id] = expiry

        video_id = context.user_data.get("video_id")
        if video_id:
            try:
                await context.bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=SOURCE_CHANNEL,
                    message_id=int(video_id)
                )
                await update.message.reply_text(
                    "✅ Verified for 24h!\n\nHere is your lecture 📖\n\nContact @catalystteamofficial (Admin)"
                )
            except Exception as e:
                await update.message.reply_text(
                    f"✅ Verified but ❌ video not found (ID: {video_id})\nError: {e}"
                )
        else:
            await update.message.reply_text(
                "✅ Verified for 24h!\n\nNow you can request your lecture again."
            )
        return

    # Agar normally start kare
    video_id = None
    if text == "/start":
        await update.message.reply_text(
            "👉 Go to https://mission-catalyst.blogspot.com\n"
            "Select your class, subject, chapter, and lecture.\n"
            "Then click on *Watch Lecture* and send me that lecture id like:\n\n"
            "`/start 302`\n\n"
            "⚠️ Example: Agar video ka message ID 104 hai to aap likhen `/start 104`",
            parse_mode="Markdown"
        )
        return

    if " " in text:
        video_id = text.split(" ", 1)[-1].strip()

    if not video_id or not video_id.isdigit():
        await update.message.reply_text(
            "❌ Invalid video id.\nUsage: `/start 302`\n\n⚠️ Example: `/start 104`",
            parse_mode="Markdown"
        )
        return

    context.user_data["video_id"] = video_id

    keyboard = [
        [InlineKeyboardButton("📢 Join Telegram Channel", url="https://t.me/shivamkmrthakur")],
        [InlineKeyboardButton("🔔 Subscribe YouTube", url="https://www.youtube.com/@missioncatalyst")],
        [InlineKeyboardButton("✅ Joined", callback_data="joined")]
    ]
    await update.message.reply_text(
        "⚠️ Please join our *Telegram channel* and *Subscribe YouTube channel* first.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# Handle Joined button
async def joined_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    video_id = context.user_data.get("video_id")

    if not video_id:
        await query.edit_message_text("❌ No video id found. Please use /start 302 again.")
        return

    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            keyboard = [
                [InlineKeyboardButton("🔔 Subscribe YouTube", url="https://www.youtube.com/@missioncatalyst")],
                [InlineKeyboardButton("✅ Subscribed", callback_data="subscribed")]
            ]
            await query.edit_message_text(
                "✅ You joined the Telegram channel!\n\nNow please *Subscribe YouTube* and confirm.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text("❌ You have not joined the Telegram channel yet.")
    except:
        await query.edit_message_text("❌ Error checking channel membership.")


# Handle Subscribed button → send second verification link
async def subscribed_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    task_link = "https://shrinkme.top/verifybot24h"
    await query.edit_message_text(
        f"✅ You subscribed YouTube!\n\nNow complete second task:\n{task_link}\n\n"
        "After completing, you’ll be redirected back to me for 24h verification."
    )


if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(joined_callback, pattern="joined"))
    app.add_handler(CallbackQueryHandler(subscribed_callback, pattern="subscribed"))

    print("Bot is running...")
    app.run_polling()
