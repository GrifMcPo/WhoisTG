import os
import asyncio
import random
import requests
import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== КОНФИГ =====
TOKEN = os.getenv("BOT_TOKEN")  # Твой токен

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Отправляет .команду и редактирует её в финальный текст"""
    cmd = update.message.text.split()[0] if update.message.text else ".command"
    sent = await update.message.reply_text(cmd)
    await sent.edit_text(text, parse_mode="Markdown")

def get_user_info(update: Update):
    user = update.message.from_user
    return f"👤 **Информация о пользователе:**\n\n• ID: `{user.id}`\n• Имя: {user.first_name}\n• Юзернейм: @{user.username if user.username else 'нет'}\n• Язык: {user.language_code}"

# ===== ОБРАБОТЧИКИ КОМАНД =====

# .help — список команд
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 **Список команд:**\n\n"
        "**Профиль:**\n"
        ".info — Информация о собеседнике\n"
        ".ping — Задержка ответа бота\n\n"
        "**Развлечения:**\n"
        ".cat — Случайное фото кота\n"
        ".coin — Орёл или Решка\n"
        ".spam <текст> — Спам текстом (10 раз)\n"
        ".typing — Анимация печати текста\n\n"
        "**Игры:**\n"
        ".rps <камень/ножницы/бумага> — Игра с ботом\n"
        ".ttt — Крестики-нолики (начать игру)\n\n"
        "**Информация:**\n"
        ".help — Показать это сообщение\n"
        ".status — Статус бота\n"
        ".repo <ссылка> — Подключить репозиторий (заглушка)"
    )
    await edit_message(update, context, text)

# .info — инфо о собеседнике
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_user_info(update)
    await edit_message(update, context, text)

# .ping — задержка
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = datetime.datetime.now()
    sent = await update.message.reply_text(".ping")
    end = datetime.datetime.now()
    delta = (end - start).total_seconds() * 1000
    await sent.edit_text(f"🏓 Pong! {delta:.0f}ms")

# .cat — фото кота
async def cat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent = await update.message.reply_text(".cat")
    try:
        response = requests.get("https://api.thecatapi.com/v1/images/search")
        url = response.json()[0]["url"]
        await sent.edit_text(f"🐱 Вот твой кот:\n{url}")
    except:
        await sent.edit_text("❌ Не удалось загрузить фото кота")

# .coin — орёл/решка
async def coin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = random.choice(["🦅 Орёл", "🪙 Решка"])
    await edit_message(update, context, f"🎲 {result}!")

# .spam — спам текстом
async def spam_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent = await update.message.reply_text(".spam")
    text = update.message.text.replace(".spam", "").strip()
    if not text:
        await sent.edit_text("❌ Укажи текст для спама: `.spam Привет!`")
        return
    for i in range(10):
        await update.message.reply_text(f"{i+1}. {text}")
        await asyncio.sleep(0.5)
    await sent.edit_text(f"✅ Отправлено 10 сообщений с текстом: `{text}`")

# .typing — анимация печати
async def typing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent = await update.message.reply_text(".typing")
    await update.message.chat.send_action(action="typing")
    await asyncio.sleep(3)
    await sent.edit_text("✅ Анимация печати завершена!")

# .rps — камень ножницы бумага
async def rps_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent = await update.message.reply_text(".rps")
    choice = update.message.text.replace(".rps", "").strip().lower()
    bot_choice = random.choice(["камень", "ножницы", "бумага"])
    
    if choice not in ["камень", "ножницы", "бумага"]:
        await sent.edit_text("❌ Выбери: `.rps камень` / `.rps ножницы` / `.rps бумага`")
        return
    
    if choice == bot_choice:
        result = "🤝 Ничья!"
    elif (choice == "камень" and bot_choice == "ножницы") or \
         (choice == "ножницы" and bot_choice == "бумага") or \
         (choice == "бумага" and bot_choice == "камень"):
        result = "🎉 Ты победил!"
    else:
        result = "😈 Бот победил!"
    
    await sent.edit_text(f"🗿 Ты: {choice}\n🤖 Бот: {bot_choice}\n\n{result}")

# .status — статус
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📊 **Статус бота:**\n\n"
        f"• Бот: @{context.bot.username}\n"
        "• GitHub: подключён\n"
        f"• Время: {datetime.datetime.now().strftime('%H:%M:%S')}"
    )
    await edit_message(update, context, text)

# .repo — подключить репозиторий (заглушка)
async def repo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent = await update.message.reply_text(".repo")
    url = update.message.text.replace(".repo", "").strip()
    if not url:
        await sent.edit_text("❌ Укажи ссылку: `.repo https://github.com/user/repo`")
        return
    await sent.edit_text(f"✅ Репозиторий подключён: {url}")

# .ttt — крестики-нолики (заглушка)
ttt_games = {}

async def ttt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in ttt_games:
        await edit_message(update, context, "❌ У тебя уже есть активная игра!")
        return
    ttt_games[user_id] = {"board": [" "]*9, "turn": "X", "winner": None}
    await edit_message(update, context, "🎮 **Крестики-нолики!**\n\nТвой ход (X).\nОтправь номер клетки (1-9):\n\n1️⃣ 2️⃣ 3️⃣\n4️⃣ 5️⃣ 6️⃣\n7️⃣ 8️⃣ 9️⃣")

# ===== ОСНОВНАЯ ФУНКЦИЯ =====
def main():
    app = Application.builder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("cat", cat_command))
    app.add_handler(CommandHandler("coin", coin_command))
    app.add_handler(CommandHandler("spam", spam_command))
    app.add_handler(CommandHandler("typing", typing_command))
    app.add_handler(CommandHandler("rps", rps_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("repo", repo_command))
    app.add_handler(CommandHandler("ttt", ttt_command))

    print("🚀 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
