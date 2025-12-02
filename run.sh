#!/bin/bash

# Скрипт запуска для Linux

# Получаем абсолютный путь к директории скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Проверка виртуального окружения
if [ -d "venv" ]; then
    echo "Активация виртуального окружения..."
    source venv/bin/activate
fi

# Проверка зависимостей
if ! python3 -c "import requests" &> /dev/null; then
    echo "Установка зависимостей..."
    pip install requests python-dotenv
fi

# Запуск программы
python3 main.py

# Деактивация виртуального окружения
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
