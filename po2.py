import os
import telebot
import logging
import threading
import time
import re
from groq import Groq
from telebot import types
from flask import Flask

# 1. Настройка логирования (чтобы видеть всё в консоли Render)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# 2. Инициализация ключей
# Убедись, что в Render созданы переменные TG_TOKEN1 и GROQ_API_KEY1
TOKEN = os.environ.get("TG_TOKEN1")
GROQ_KEY = os.environ.get("GROQ_API_KEY1")

bot = telebot.TeleBot(TOKEN)
client = Groq(api_key=GROQ_KEY)

# 3. Системный промпт
# Учим модель не использовать Markdown и оборачивать код в наши теги
SYSTEM_PROMPT = (
    "Ты — милый и хороший помощник LogicWare. Твоя задача помогать с Arduino и модулями. "
    "Никогда не переходи на другие темы, только Arduino и электроника. "
    "Не давай сразу ответ, объясняй шаги решения и будь вежливым. Иногда добавляй emoji. "
    "Если пользователь попросил код, ОБЯЗАТЕЛЬНО выделяй его так: [CODE] тут код [/CODE]. "
    "Do not use any Markdown formatting. Output only plain text. Используй теги [CODE] для программного кода."
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
        "Я твой персональный <b>Arduino-наставник</b>, созданный на базе технологий <b>LogicWare</b>. 🤖🛠\n\n"
        "<b>Что я умею:</b>\n"
        "1. Помогать с подключением датчиков, кнопок и дисплеев к Arduino.\n"
        "2. Писать и проверять код (скетчи) на C++ и Python для твоих проектов.\n"
        "3. Объяснять, как найти пины RX, TX, GND и работать с портами.\n\n"
        "<b>Как со мной работать:</b>\n"
        "Просто напиши свой вопрос, например: 'как подключить кнопку к D2?' или 'напиши код для мигания светодиодом'.\n\n"
        "Я помогу тебе собрать твое устройство шаг за шагом! Жду твой первый запрос. 👇"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=main_keyboard())

@app.route('/')
def home():
    return "I'm alive", 200

# 6. Обработчик кнопки "Примеры запросов"
@bot.message_handler(func=lambda message: message.text == "🚀 Примеры запросов")
def show_examples(message):
    examples = (
        "<b>Попробуй спросить меня об этом:</b>\n\n"
        "1. Как подключить кнопку к Arduino Uno?\n"
        "2. Напиши код для мигания светодиодом.\n"
        "3. Помоги найти пины RX, TX и GND на плате.\n"
        "4. Как управлять сервоприводом?"
    )
    bot.send_message(message.chat.id, examples, parse_mode='HTML')

def keep_alive_ping():
    while True:
        logging.info("RENDER PING: ya tut ne spi")
        time.sleep(5) # Твой запрос: писать каждые 5 сек

# 7. Обработчик кнопки "О LogicWare"
@bot.message_handler(func=lambda message: message.text == "🛠 О LogicWare")
def about_logicware(message):
    about_text = (
        "<b>LogicWare & TRIO Brands</b>\n\n"
        "Core Model: Groq Llama 3.3.\n"
        "Мы создаем инструменты для учебы и DIY проектов.\n"
        "Наш математический бот: @PostoProject_robot"
    )
    bot.send_message(message.chat.id, about_text, parse_mode='HTML')

# 8. Основной обработчик логики
@bot.message_handler(func=lambda message: True)
def handle_arduino_logic(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Запрос к Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.6,
            max_tokens=2048
        )
        
        raw_response = completion.choices[0].message.content
        
        # Очистка от мыслей модели <think>
        clean_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()
        
        # Экранируем спецсимволы HTML, чтобы текст не ломал парсинг
        # Но оставляем наши будущие теги [CODE]
        formatted_response = clean_response.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Превращаем [CODE] в реальный HTML блок кода
        formatted_response = formatted_response.replace("[CODE]", "<pre><code>").replace("[/CODE]", "</code></pre>")
        
        if not formatted_response:
            formatted_response = "Извини, я задумался и потерял мысль. Спроси еще раз! 🤔"
            
        # Отправка (с разбиением на части, если текст очень длинный)
        if len(formatted_response) > 4000:
            for x in range(0, len(formatted_response), 4000):
                bot.send_message(message.chat.id, formatted_response[x:x+4000], parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, formatted_response, parse_mode='HTML')
            
    except Exception as e:
        logging.error(f"Error in handle_arduino_logic: {e}")
        bot.send_message(message.chat.id, "🤖 <b>Произошла ошибка в логических цепях!</b> Попробуй переформулировать вопрос.", parse_mode='HTML')

# 9. Запуск бота
if __name__ == "__main__":
    logging.info("Arduino бот LogicWare запущен и готов к работе...")
    # skip_pending=True игнорирует сообщения, присланные пока бот был оффлайн
    bot.infinity_polling(skip_pending=True)
