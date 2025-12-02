@echo off
REM start_simple.bat
REM Простой скрипт запуска

chcp 65001 >nul
cls

echo.
echo ========================================
echo    VK Moosic Player Console
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.6+ и добавьте в PATH
    pause
    exit /b 1
)

REM Проверка зависимостей
echo Проверка зависимостей...
python -c "import requests, dotenv" 2>nul
if errorlevel 1 (
    echo Установка необходимых библиотек...
    pip install requests python-dotenv 2>nul || python -m pip install requests python-dotenv
)

REM Запуск
echo.
echo Запуск программы...
echo.
python main.py

REM Пауза если ошибка
if errorlevel 1 pause