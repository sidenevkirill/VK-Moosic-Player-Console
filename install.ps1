# install.ps1
# Скрипт установки для PowerShell

# Установка UTF-8 кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Установка VK Moosic Player Console   " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка Python
Write-Host "Проверка установки Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python не найден"
    }
} catch {
    Write-Host "ОШИБКА: Python не найден!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Установите Python 3.6 или выше:" -ForegroundColor Yellow
    Write-Host "1. Перейдите на https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "2. Скачайте и установите Python" -ForegroundColor White
    Write-Host "3. Обязательно отметьте 'Add Python to PATH'" -ForegroundColor White
    Write-Host ""
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host ""

# Проверка pip
Write-Host "Проверка установки pip..." -ForegroundColor Yellow
try {
    $pipVersion = python -m pip --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: $($pipVersion[0])" -ForegroundColor Green
    } else {
        throw "pip не найден"
    }
} catch {
    Write-Host "ВНИМАНИЕ: pip не найден" -ForegroundColor Yellow
    Write-Host "Установка pip..." -ForegroundColor Yellow
    
    # Скачиваем get-pip.py
    Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "get-pip.py"
    
    if (Test-Path "get-pip.py") {
        python get-pip.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ОШИБКА: Не удалось установить pip" -ForegroundColor Red
            Remove-Item "get-pip.py" -Force -ErrorAction SilentlyContinue
            Read-Host "Нажмите Enter для выхода"
            exit 1
        }
        Remove-Item "get-pip.py" -Force -ErrorAction SilentlyContinue
        Write-Host "OK: pip установлен" -ForegroundColor Green
    }
}

Write-Host ""

# Установка зависимостей
Write-Host "Установка зависимостей Python..." -ForegroundColor Yellow

# Создаем requirements.txt
@"
requests>=2.31.0
python-dotenv>=1.0.0
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8

# Обновляем pip
python -m pip install --upgrade pip

# Устанавливаем зависимости
python -m pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Не удалось установить зависимости" -ForegroundColor Red
    Write-Host "Попробуйте установить вручную:" -ForegroundColor Yellow
    Write-Host "python -m pip install requests python-dotenv" -ForegroundColor White
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "OK: Зависимости установлены" -ForegroundColor Green
Write-Host ""

# Создаем скрипт запуска
Write-Host "Создание скрипта запуска..." -ForegroundColor Yellow
@'
@echo off
chcp 65001 >nul
cls
echo.
echo ========================================
echo    VK Moosic Player Console
echo ========================================
echo.
python main.py
if errorlevel 1 pause
'@ | Out-File -FilePath "start.bat" -Encoding ASCII

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!       " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Для запуска программы:" -ForegroundColor Yellow
Write-Host "  Дважды кликните по start.bat" -ForegroundColor White
Write-Host "  Или запустите в PowerShell: .\start.bat" -ForegroundColor White
Write-Host ""
Write-Host "Перед первым запуском:" -ForegroundColor Yellow
Write-Host "  Создайте файл vk_token.txt с токеном VK" -ForegroundColor White
Write-Host "  Или введите токен в программе" -ForegroundColor White
Write-Host ""
Read-Host "Нажмите Enter для завершения"