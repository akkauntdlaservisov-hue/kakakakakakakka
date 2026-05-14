import os
import telebot
import logging
import re
from groq import Groq
from telebot import types

# 1. Настройка логирования
logging.basicConfig(level=logging.INFO)

# 2. Инициализация ключей
TOKEN = os.environ.get("TG_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_KEY)

# 3. Системный промпт
SYSTEM_PROMPT = (
    "Ты — милый и хороший помощник. Твоя задача решать математические задачи. "
    "Не давай сразу ответ, объясняй шаги решения и будь вежливым. "
    "Если задача очень простая, отвечай быстро. Если сложная — расписывай подробно. I ispolzuy pochashe emoji "
    "Do not use any Markdown formatting in your responses. Output only plain text, esli vse taki budesh, to tvoy parse mode eto html."
)

# 4. Клавиатура с кнопками
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Примеры запросов")
    btn2 = types.KeyboardButton("🛠 О LogicWare")
    markup.add(btn1, btn2)
    return markup

# 5. Обработчик команды /start
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я твой персональный **Математический Решатель**, созданный на базе технологий **LogicWare**. 🧠✨\n\n"
        "**Что я умею:**\n"
        "1. Решать арифметические примеры (от простых до самых сложных).\n"
        "2. Объяснять логику решения шаг за шагом (я не просто кидаю ответ!).\n"
        "3. Помогать с алгеброй, геометрией и даже программированием.\n\n"
        "**Как со мной работать:**\n"
        "Просто напиши мне любой пример, например: `(15 * 4) / 2 + 7` или `реши уравнение x^2 = 16`.\n\n"
        "Я постараюсь быть максимально полезным, добрым и понятным! Жду твой первый запрос. 👇"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=main_keyboard())

# 6. Обработчик кнопки "Примеры запросов"
@bot.message_handler(func=lambda message: message.text == "🚀 Примеры запросов")
def show_examples(message):
    examples = (
        "Попробуй отправить мне что-то такое:\n\n"
        "1. `Реши уравнение x^2 - 5x + 6 = 0`\n"
        "2. `Сколько будет 15% от 4500?`\n"
        "3. `Найди производную функции y = x^3`"
    )
    bot.send_message(message.chat.id, examples, parse_mode='HTML')

# 7. Обработчик кнопки "О LogicWare"
@bot.message_handler(func=lambda message: message.text == "🛠 О LogicWare")
def about_logicware(message):
    bot.send_message(message.chat.id, "Core Model: Groq AI. Developed under TRIO & LogicWare brands. We and have a second bot, @MostoProject_robot. This is a bot for arduino.")

# 8. Основной обработчик текста и математики
@bot.message_handler(func=lambda message: True)
def handle_math(message):
    user_query = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Запрос к нейросети (используем рабочую модель)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            temperature=0.6,
            max_tokens=2048
        )
        
        raw_response = completion.choices[0].message.content
        
        # УДАЛЕНИЕ ТЕГОВ <think> И ВСЕГО ИХ СОДЕРЖИМОГО
        clean_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()
        
        # Если ответ оказался пустым после очистки
        if not clean_response:
            clean_response = "Извини, я задумался и не смог сформулировать ответ. Попробуй еще раз!"
            
        # Отправка ответа пользователю с учетом лимита символов в Telegram
        if len(clean_response) > 4000:
            for x in range(0, len(clean_response), 4000):
                bot.send_message(message.chat.id, clean_response[x:x+4000], parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, clean_response, parse_mode='HTML')
            
    except Exception as e:
        bot.send_message(message.chat.id, "Ой, что-то пошло не так при решении... попробуй еще раз!")
        logging.error(f"Error API: {e}")

# 9. Безопасный запуск бота
if __name__ == "__main__":
    logging.info("Бот запущен и готов к работе...")
    # skip_pending=True решает проблему ошибки 409 Conflict при перезапуске
    bot.infinity_polling(skip_pending=True)
