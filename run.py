import subprocess
import sys
import os
import time
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "LogicWare Multi-Bot System is Live", 200

def start_bots():
    # Запускаем процессы без блокировки через .wait() сразу
    # Каждый файл занимается только своим ботом
    processes = []
    scripts = ["po1.py", "po2.py", "po3.py"]
    
    for script in scripts:
        logging.info(f"Запуск {script}...")
        p = subprocess.Popen([sys.executable, script])
        processes.append(p)
    return processes

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    # 1. Запускаем всех ботов
    bot_processes = start_bots()

    # 2. Запускаем Flask на порту Render
    # Это единственный процесс, который занимает порт!
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
