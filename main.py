import os
import telebot
import logging
from groq import Groq
from telebot import types

# 1. Настройка логирования (чтобы видеть ошибки в консоли Render)
logging.basicConfig(level=logging.INFO)

# 2. Инициализация ключей
# ВАЖНО: На Render в разделе Environment Variables создай переменные с этими именами
TOKEN = os.environ.get("TG_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_KEY)

# 3. Системный промпт (личность твоего бота)
SYSTEM_PROMPT = (
    "Ты — лучший в мире математический помощник от LogicWare. "
    "Ты очень милый, добрый и используешь эмодзи. "
    "Твоя задача: решать задачи пошагово. Никогда не давай только ответ. "
    "Объясняй так, чтобы понял даже ребенок. Используй Markdown для оформления формул."
)

# Функция для создания кнопок
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Примеры запросов")
    btn2 = types.KeyboardButton("🛠 О LogicWare")
    markup.add(btn1, btn2)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        f"🌟 **Привет, {message.from_user.first_name}!**\n\n"
        "Я — твой интеллектуальный наставник по математике. "
        "Моя цель не просто решить пример, а научить тебя понимать его!\n\n"
        "✨ **Что я могу:**\n"
        "• Разложить сложное уравнение по полочкам.\n"
        "• Объяснить теоремы и правила.\n"
        "• Помочь с кодом на Python или C.\n\n"
        "Просто напиши свой вопрос ниже! 👇"
    )
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode='Markdown', 
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "🚀 Примеры запросов")
def show_examples(message):
    examples = (
        "Попробуй отправить мне что-то такое:\n\n"
        "1. `Реши уравнение x^2 - 5x + 6 = 0`\n"
        "2. `Сколько будет 15% от 4500?`\n"
        "3. `Найди производную функции y = x^3`"
    )
    bot.send_message(message.chat.id, examples, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🛠 О LogicWare")
def about_logicware(message):
    bot.send_message(message.chat.id, "Core Model: Gemini 3 Flash. Developed under TRIO & LogicWare brands.")

# 4. Основной обработчик запросов
@bot.message_handler(func=lambda message: True)
def handle_ai_request(message):
    # Эффект "печать..." в Telegram, чтобы юзер не скучал
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Запрос к Groq с использованием модели Llama 3
        completion = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.6, # Чуть меньше креативности для точности в математике
            max_tokens=2048
        )
        
        response_text = completion.choices[0].message.content
        
        # Разбиваем длинные сообщения (лимит TG - 4096 символов)
        if len(response_text) > 4000:
            for x in range(0, len(response_text), 4000):
                bot.send_message(message.chat.id, response_text[x:x+4000], parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, response_text, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        bot.send_message(message.chat.id, "🤖 Мои нейронные цепи перегрелись! Попробуй переформулировать запрос.")

# 5. Запуск
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
