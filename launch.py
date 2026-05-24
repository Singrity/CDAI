import subprocess
import sys
import os
import webbrowser
import time
import urllib.request

REQUIRED_PACKAGES = ["fastapi", "uvicorn", "jinja2", "pydantic"]
SERVER_URL = "http://127.0.0.1:8000"


def install_deps():
    """Устанавливает недостающие пакеты через pip."""
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"📦 Устанавливаю {pkg}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet", pkg]
            )


def prepare_dirs():
    """Создаёт структуру папок, если её нет."""
    os.makedirs("front/templates", exist_ok=True)
    os.makedirs("front/static", exist_ok=True)
    if not os.path.isfile("main.py"):
        print("❌ Ошибка: файл main.py не найден в текущей директории!")
        input("Нажмите Enter для выхода...")
        sys.exit(1)


def wait_for_server(timeout=20):
    """Ждёт, пока сервер начнёт отвечать на GET-запросы."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(SERVER_URL, timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def main():
    print("🔍 Проверка зависимостей...")
    install_deps()

    print("📁 Подготовка проекта...")
    prepare_dirs()

    print("🚀 Запуск сервера...")
    # Запускаем uvicorn в отдельном процессе
    server_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--log-level",
            "info",
        ]
    )

    print("⏳ Ожидание готовности сервера...")
    if wait_for_server():
        print("✅ Сервер готов! Открываю браузер...")
        webbrowser.open(SERVER_URL)
    else:
        print("⚠️ Сервер не ответил вовремя. Проверьте вывод консоли выше.")

    try:
        print("🟢 Калькулятор работает. Чтобы остановить, нажмите Ctrl+C.")
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")
        server_proc.terminate()
        server_proc.wait()


if __name__ == "__main__":
    main()
