import subprocess
import sys
import os
import time
import threading
import logging
from flask import Flask

# 1. Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = Flask(__name__)

@app.route('/')
def home():
    return "LogicWare Multi-Bot System is Live and Monitoring", 200

def monitor_bot(script_name):
    """Функция следит за ботом и перезапускает его при вылете"""
    while True:
        logging.info(f"--- Запуск процесса: {script_name} ---")
        try:
            # Запускаем скрипт
            process = subprocess.Popen([sys.executable, script_name])
            
            # Ждем завершения процесса (если он упадет)
            exit_code = process.wait()
            
            logging.error(f"!!! Файл {script_name} завершился с кодом {exit_code}. Перезапуск через 5 секунд...")
        except Exception as e:
            logging.error(f"!!! Ошибка при запуске {script_name}: {e}")
        
        time.sleep(5)

if __name__ == "__main__":
    # Список твоих файлов
    scripts = ["po1.py", "po2.py", "po3.py"]

    # 2. Запускаем мониторинг каждого бота в отдельном потоке
    for script in scripts:
        if os.path.exists(script):
            t = threading.Thread(target=monitor_bot, args=(script,), daemon=True)
            t.start()
        else:
            logging.warning(f"Файл {script} не найден в директории!")

    # 3. Запускаем Flask на порту Render
    # Это основной поток, который не дает сервису закрыться
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"Старт веб-интерфейса на порту {port}")
    
    # Режим debug=False обязателен для работы в потоках на Render
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
