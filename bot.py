import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Завантажуємо .env локально
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None

pending_quotes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Надішліть мені цитату, я передам її на модерацію.")

async def handle_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        return

    pending_quotes[update.message.message_id] = text

    keyboard = [
        [
            InlineKeyboardButton("✅ Одобрити", callback_data=f"approve:{update.message.message_id}"),
            InlineKeyboardButton("❌ Відхилити", callback_data=f"reject:{update.message.message_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Нова цитата:\n\n{text}",
        reply_markup=reply_markup
    )
    await update.message.reply_text("✅ Цитату відправлено на модерацію.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, msg_id = query.data.split(":")
    msg_id = int(msg_id)

    if action == "approve":
        text = pending_quotes.get(msg_id, "")
        if text:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
            await query.edit_message_text(text=f"✅ Опубліковано:\n\n{text}")
    elif action == "reject":
        await query.edit_message_text(text="❌ Відхилено")

def main():
    if not TOKEN or not ADMIN_ID or not CHANNEL_ID:
        raise RuntimeError("BOT_TOKEN, ADMIN_ID або CHANNEL_ID не задані як змінні середовища.")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quote))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot started and polling ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
