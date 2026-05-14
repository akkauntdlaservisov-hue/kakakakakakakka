import subprocess
import sys

# Запускаем оба файла одновременно
p1 = subprocess.Popen([sys.executable, "po2.py"])
p2 = subprocess.Popen([sys.executable, "po1.py"])

# Ждем завершения (они будут работать бесконечно)
p1.wait()
p2.wait()
