from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

import instaloader

# Твои данные (уже вшиты)
TELEGRAM_TOKEN = "8249240275:AAG6XeIq_brTL1r9XZvgdo27yxFb9PDUK84"
INSTA_USERNAME = "mot_avia"
INSTA_PASSWORD = "tema2007A"

# === Обработка /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь ссылку на Instagram профиль или пост.")

# === Получение ссылки и кнопки ===
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    context.user_data["insta_url"] = url

    keyboard = [
        [InlineKeyboardButton("📌 Подписчики", callback_data="followers")],
        [InlineKeyboardButton("🔥 Актив с постов", callback_data="likers")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Что парсить?", reply_markup=reply_markup)

# === Парсинг ===
async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data
    url = context.user_data.get("insta_url", "")
    username = url.strip("/").split("/")[-1]

    await query.edit_message_text(f"🔍 Начинаю парсинг @{username}...")

    try:
        L = instaloader.Instaloader()
        L.login(INSTA_USERNAME, INSTA_PASSWORD)
        profile = instaloader.Profile.from_username(L.context, username)

        result = set()

        if action == "followers":
            for follower in profile.get_followers():
                result.add(f"@{follower.username}")
        elif action == "likers":
            posts = profile.get_posts()
            for post in posts:
                for liker in post.get_likes():
                    result.add(f"@{liker.username}")
                break  # только первый пост

        output = "\n".join(sorted(result)) or "Ничего не найдено"
        await query.message.reply_text(f"🎯 Результат:\n{output[:4000]}")
    except Exception as e:
        await query.message.reply_text(f"⚠️ Ошибка: {str(e)}")

# === Запуск бота ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(handle_action))

    app.run_polling()

if __name__ == "__main__":
    main()
