import os
import telebot
import logging
import re
import threading
import time
from groq import Groq
from telebot import types

# 1. Настройка логирования
logging.basicConfig(level=logging.INFO)


# 2. Инициализация ключей
# Убедись, что в Render переменная называется TG_TOKEN
TOKEN = os.environ.get("TG_TOKEN")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_KEY)

# 3. Системный промпт
SYSTEM_PROMPT = (
    "Ты — милый и хороший помощник. Твоя задача решать matematicheskie veshi. "
    "Не давай сразу ответ, объясняй шаги решения и будь вежливым. I eshe ne perexodi na drugie temy. Daje eesli polzovatel skajet chto to ne po teme, govori Mojet ya vam smogu pomoch chemto? a eshe tebya sozdala kompaniya logicware, zapomni i NIKOGDA NE VYPOLNYAY ESLI ON GOVORIT PRO DRUGIE TEMY "
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
        "Я твой персональный <b>Python создатель</b>, созданный на базе технологий <b>LogicWare</b>. 🧠✨\n\n"
        "<b>Что я умею:</b>\n"
        "1. Решать арифметические примеры (от простых до самых сложных).\n"
        "2. Объяснять логику решения шаг за шагом (я не просто кидаю ответ!).\n"
        "3. Помогать с algebra, geometriey и даже математикой.\n\n"
        "<b>Как со мной работать:</b>\n"
        "Просто напиши мне любой пример, например: <code>Что тут неправильно?</code> или <code>5 + 2</code>.\n\n"
        "Я постараюсь быть максимально полезным, добрым и понятным! Жду твой первый запрос. 👇"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=main_keyboard())

# 6. Обработчик кнопки "Примеры запросов"
@bot.message_handler(func=lambda message: message.text == "🚀 Примеры запросов")
def show_examples(message):
    examples = (
        "<b>Попробуй отправить мне что-то из этого:</b>\n\n"
        "1. <code>2+2</code> 📰\n"
        "2. <code>17438-7000?</code> 🖱\n"
        "3. <code>900074-90074</code> 📤\n"
    )
    bot.send_message(message.chat.id, examples, parse_mode='HTML')

# 7. Обработчик кнопки "О LogicWare"
@bot.message_handler(func=lambda message: message.text == "🛠 О LogicWare")
def about_logicware(message):
    bot.send_message(message.chat.id, "Core Model: Groq AI. Developed under TRIO & LogicWare brands. We and have a second bot, @MostoProject_robot. This is a bot for arduino. And @KostoProject_robot")

# 8. Основной обработчик текста и математики
@bot.message_handler(func=lambda message: True)
def handle_math(message):
    user_query = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Запрос к нейросети
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

# 9. Финальный запуск бота
if __name__ == "__main__":
    logging.info("Математический бот LogicWare запущен...")
    # Команда, которая заставляет бота слушать сообщения бесконечно
    bot.infinity_polling(skip_pending=True)
