@echo off
chcp 65001 >nul
REM install_dependencies.bat
REM Скрипт установки зависимостей для Windows

echo ========================================
echo    Установка VK Moosic Player Console
echo ========================================
echo.

REM Проверка Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден!
    echo Установите Python 3.6 или выше с сайта python.org
    echo и добавьте Python в PATH при установке
    pause
    exit /b 1
)

python --version
if errorlevel 1 (
    echo [ERROR] Ошибка при проверке версии Python
    pause
    exit /b 1
)

REM Проверка pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] pip не найден
    echo Установка pip...
    
    REM Скачиваем get-pip.py
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')"
    
    if exist get-pip.py (
        echo Запуск установки pip...
        python get-pip.py
        
        if errorlevel 1 (
            echo [ERROR] Ошибка при установке pip
            del get-pip.py 2>nul
            pause
            exit /b 1
        )
        
        del get-pip.py
        echo [INFO] pip успешно установлен
        
        REM Обновляем PATH
        setx PATH "%PATH%;%APPDATA%\Python\Python39\Scripts" >nul 2>&1
        echo [INFO] Перезапустите консоль для применения изменений PATH
    ) else (
        echo [ERROR] Не удалось скачать get-pip.py
        echo Установите pip вручную:
        echo 1. Скачайте https://bootstrap.pypa.io/get-pip.py
        echo 2. Выполните: python get-pip.py
        pause
        exit /b 1
    )
)

REM Создание requirements.txt
if not exist requirements.txt (
    echo [INFO] Создание файла requirements.txt...
    (
        echo requests^>=2.31.0
        echo python-dotenv^>=1.0.0
    ) > requirements.txt
)

REM Установка зависимостей
echo [INFO] Установка зависимостей...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Ошибка при установке зависимостей
    echo Попробуйте установить вручную:
    echo python -m pip install requests python-dotenv
    pause
    exit /b 1
)

REM Создание скрипта запуска
echo [INFO] Создание скрипта запуска...
(
    echo @echo off
    echo chcp 65001 ^>nul
    echo echo ========================================
    echo echo    VK Moosic Player Console
    echo echo ========================================
    echo echo.
    echo python main.py
    echo pause
) > run.bat

echo.
echo ========================================
echo    Установка завершена успешно!
echo ========================================
echo.
echo Для запуска программы выполните:
echo   run.bat
echo.
echo Перед первым запуском создайте файл vk_token.txt
echo с вашим токеном VK или введите его в программе
echo.
pause