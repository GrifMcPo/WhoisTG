import os
import asyncio
import random
import requests
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== КОНФИГ =====
TOKEN = os.getenv("BOT_TOKEN")  # Твой токен
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra")

# ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====
async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Отправляет .команду и редактирует её в финальный текст"""
    sent = await update.message.reply_text(f".{update.message.text.split()[0]}")
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
        "**AI-функции:**\n"
        ".gpt <вопрос> — Вопрос нейросети\n"
        ".image <запрос> — Генерация изображения\n"
        ".a_gpt — Включить автоответ нейросетью\n"
        ".a_gpt_off — Выключить автоответ\n\n"
        "**Игры:**\n"
        ".rps <камень/ножницы/бумага> — Игра с ботом\n"
        ".ttt — Крестики-нолики (начать игру)\n\n"
        "**Информация:**\n"
        ".help — Показать это сообщение\n"
        ".status — Статус репозитория\n"
        ".repo <ссылка> — Подключить репозиторий"
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

# .gpt — вопрос нейросети
async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent = await update.message.reply_text(".gpt")
    question = update.message.text.replace(".gpt", "").strip()
    if not question:
        await sent.edit_text("❌ Укажи вопрос: `.gpt Как дела?`")
        return
    await sent.edit_text("🤔 Думаю...")
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": question}]
            }
        )
        answer = response.json()["choices"][0]["message"]["content"]
        await sent.edit_text(f"🤖 **Ответ:**\n\n{answer}")
    except Exception as e:
        await sent.edit_text(f"❌ Ошибка: {e}")

# .image — генерация изображения
async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent = await update.message.reply_text(".image")
    prompt = update.message.text.replace(".image", "").strip()
    if not prompt:
        await sent.edit_text("❌ Укажи запрос: `.image кот в шляпе`")
        return
    await sent.edit_text("🎨 Генерирую изображение...")
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/dall-e-3",
                "messages": [{"role": "user", "content": f"Сгенерируй изображение: {prompt}"}]
            }
        )
        # OpenRouter DALL-E через chat completions возвращает текст с ссылкой
        answer = response.json()["choices"][0]["message"]["content"]
        await sent.edit_text(f"🖼️ **Запрос:** {prompt}\n\n{answer}")
    except Exception as e:
        await sent.edit_text(f"❌ Ошибка: {e}")

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
        f"• Модель: {OPENROUTER_MODEL}\n"
        "• GitHub: подключён\n"
        f"• Пинг: {datetime.datetime.now().strftime('%H:%M:%S')}"
    )
    await edit_message(update, context, text)

# .repo — подключить репозиторий
async def repo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent = await update.message.reply_text(".repo")
    url = update.message.text.replace(".repo", "").strip()
    if not url:
        await sent.edit_text("❌ Укажи ссылку: `.repo https://github.com/user/repo`")
        return
    # Здесь твоя логика для GitHubManager
    await sent.edit_text(f"✅ Репозиторий подключён: {url}")

# .a_gpt — автоответ GPT
auto_gpt_enabled = {}

async def a_gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    auto_gpt_enabled[user_id] = True
    await edit_message(update, context, "✅ Автоответ GPT включён! Теперь я буду отвечать на все твои сообщения.")

async def a_gpt_off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    auto_gpt_enabled.pop(user_id, None)
    await edit_message(update, context, "❌ Автоответ GPT выключен.")

async def auto_gpt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in auto_gpt_enabled:
        return
    if not update.message.text or update.message.text.startswith("."):
        return
    await update.message.reply_text("🤔 Думаю...")
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": update.message.text}]
            }
        )
        answer = response.json()["choices"][0]["message"]["content"]
        await update.message.reply_text(f"🤖 {answer}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

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
    app.add_handler(CommandHandler("gpt", gpt_command))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(CommandHandler("rps", rps_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("repo", repo_command))
    app.add_handler(CommandHandler("a_gpt", a_gpt_command))
    app.add_handler(CommandHandler("a_gpt_off", a_gpt_off_command))
    app.add_handler(CommandHandler("ttt", ttt_command))

    # Обработчик для авто-GPT
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_gpt_handler))

    print("🚀 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
