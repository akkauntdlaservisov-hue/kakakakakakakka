import os
import telebot
import logging
import re
import threading
import time
import html
from groq import Groq
from telebot import types

# 1. Настройка логирования
logging.basicConfig(level=logging.INFO)

# 2. Инициализация ключей
# Убедись, что переменные TG_TOKEN2 и GROQ_API_KEY созданы в Render
TOKEN = os.environ.get("TG_TOKEN2")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_KEY)

# 3. Системный промпт (ОБНОВЛЕН)
SYSTEM_PROMPT = (
    "Ты — милый и хороший помощник. Твоя задача решать и создавать python программы как скажет пользователь. "
    "Не давай сразу ответ, объясняй шаги решения и будь вежливым. Не переходи на другие языки (html, nasm нельзя!!! только python). Daje eesli polzovatel skajet chto to ne po teme, govori Mojet ya vam smogu pomoch chemto? a eshe tebya sozdala kompaniya logicware, zapomni "
    "Если задача очень простая, отвечай быстро. Если сложная — расписывай подробно. Используй почаще emoji. "
    "ОБЯЗАТЕЛЬНО: Если ты пишешь кусок кода, всегда оборачивай его строго в теги [CODE] и [/CODE]. "
    "Не используй Markdown, только обычный текст и теги [CODE]."
)

# 4. Клавиатура с кнопками
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🚀 Примеры запросов")
    btn2 = types.KeyboardButton("🛠 О LogicWare")
    markup.add(btn1, btn2)
    return markup

# 5. Обработчик команды /start (ОБНОВЛЕН)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я твой персональный <b>Python создатель</b>, созданный на базе технологий <b>LogicWare</b>. 🧠✨\n\n"
        "<b>Что я умею:</b>\n"
        "1. Писать скрипты и автоматизировать рутину.\n"
        "2. Объяснять логику решения шаг за шагом (я не просто кидаю ответ!).\n"
        "3. Помогать с кодом для игр и парсеров.\n\n"
        "<b>Как со мной работать:</b>\n"
        "Просто напиши мне задачу, например: <code>Сделай автокликер на pyautogui</code>.\n\n"
        "Я постараюсь быть максимально полезным, добрым и понятным! Жду твой первый запрос. 👇"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=main_keyboard())

# 6. Обработчик кнопки "Примеры запросов" (ОБНОВЛЕН)
@bot.message_handler(func=lambda message: message.text == "🚀 Примеры запросов")
def show_examples(message):
    examples = (
        "<b>Попробуй отправить мне что-то из этого:</b>\n\n"
        "1. <code>Напиши скрипт для парсинга заголовков новостей с сайта</code> 📰\n"
        "2. <code>Как сделать автокликер на Python для нажатия кнопки каждые 2 секунды?</code> 🖱\n"
        "3. <code>Сделай Telegram-бота, который пересылает сообщения из одного канала в другой</code> 📤\n"
    )
    bot.send_message(message.chat.id, examples, parse_mode='HTML')

# 7. Обработчик кнопки "О LogicWare"
@bot.message_handler(func=lambda message: message.text == "🛠 О LogicWare")
def about_logicware(message):
    bot.send_message(message.chat.id, "Core Model: Groq AI. Developed under TRIO & LogicWare brands. We have a second bot, @PostoProject_robot. This is a bot for arduino. And @MostoProject_robot")

# 8. Основной обработчик текста и математики
@bot.message_handler(func=lambda message: True)
def handle_math(message):
    user_query = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
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
        
        # УДАЛЕНИЕ ТЕГОВ <think>
        clean_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()
        
        # ФУНКЦИЯ ДЛЯ КРАСИВОГО КОДА
        def replace_code(match):
            code = html.escape(match.group(1).strip())
            return f"<pre><code class='language-python'>{code}</code></pre>"
            
        formatted_response = re.sub(r'\[CODE\](.*?)\[/CODE\]', replace_code, clean_response, flags=re.DOTALL)
        
        if not formatted_response:
            formatted_response = "Извини, я задумался и не смог сформулировать ответ. Попробуй еще раз!"
            
        if len(formatted_response) > 4000:
            for x in range(0, len(formatted_response), 4000):
                bot.send_message(message.chat.id, formatted_response[x:x+4000], parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, formatted_response, parse_mode='HTML')
            
    except Exception as e:
        bot.send_message(message.chat.id, "Ой, что-то пошло не так при решении... попробуй еще раз!")
        logging.error(f"Error API: {e}")

# --- ФИНАЛЬНЫЙ ЗАПУСК ---
if __name__ == "__main__":
    logging.info("Python бот LogicWare запущен...")
    # Эта команда заставляет бота работать бесконечно и слушать сообщения
    bot.infinity_polling(skip_pending=True)
