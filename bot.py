import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔑 Replace with your bot token
TOKEN = "8125551108:AAFej9_9y9JieML31sjXEYFs217TddX3wmQ"

# Channel(s) to join
CHANNELS = ["@shivamkmrthakur"]

# Verification code from second task
VERIFY_CODE = "76353736"

# Store verified users with expiry
verified_users = {}  # {user_id: expiry_time}


# Check if user joined channel
async def is_subscribed(bot, user_id, channel):
    try:
        member = await bot.get_chat_member(channel, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    # If user came from verification link
    if args:
        code = args[0]
        if code == VERIFY_CODE:
            expiry = datetime.now() + timedelta(hours=24)
            verified_users[user_id] = expiry
            await update.message.reply_text(
                "✅ Verified for 24h!\n\nContact @catalystteamofficial (Admin)"
            )
        else:
            await update.message.reply_text("❌ Invalid verification link.")
        return

    # Normal start → ask to join channel
    keyboard = [[InlineKeyboardButton(f"Join {ch}", url=f"https://t.me/{ch[1:]}")] for ch in CHANNELS]
    keyboard.append([InlineKeyboardButton("✅ I Joined", callback_data="check_join")])

    await update.message.reply_text(
        "👉 Please join the required channel to continue:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# Handle button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "check_join":
        joined_all = True
        for ch in CHANNELS:
            if not await is_subscribed(context.bot, user_id, ch):
                joined_all = False
                break

        if joined_all:
            # Send second task link
            task_link = "https://shrinkme.top/verifybot24h"
            await query.edit_message_text(
                f"✅ You joined the channel!\n\nNow complete this task:\n{task_link}\n\n"
                "After completing, come back via the verification link."
            )
        else:
            await query.edit_message_text("❌ You must join the channel before continuing.")


# /status command → check if still verified
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in verified_users:
        if datetime.now() < verified_users[user_id]:
            remaining = verified_users[user_id] - datetime.now()
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            await update.message.reply_text(
                f"✅ You are verified.\nTime left: {remaining.days}d {hours}h {minutes}m"
            )
            return
        else:
            del verified_users[user_id]

    await update.message.reply_text("❌ You are not verified or your verification expired.")


# Main
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
