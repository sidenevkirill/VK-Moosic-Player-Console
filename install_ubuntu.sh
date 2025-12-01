#!/bin/bash

# install_ubuntu.sh
# Скрипт установки для Ubuntu/Linux

echo "========================================"
echo "   Установка VK Moosic Player Console   "
echo "========================================"
echo

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка на Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    print_warning "Это не Debian/Ubuntu система. Установка может потребовать ручной настройки."
fi

# Обновление системы
print_info "Обновление списка пакетов..."
sudo apt-get update

# Установка Python3 и pip
print_info "Установка Python3 и pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Проверка установки
if ! command -v python3 &> /dev/null; then
    print_error "Python3 не установился. Установите вручную:"
    echo "sudo apt-get install python3 python3-pip"
    exit 1
fi

# Проверка версии Python
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION установлен"

# Создание виртуального окружения
print_info "Создание виртуального окружения..."
python3 -m venv venv

if [ $? -eq 0 ]; then
    print_success "Виртуальное окружение создано"
else
    print_warning "Не удалось создать виртуальное окружение"
    print_info "Установка python3-venv..."
    sudo apt-get install -y python3-venv
    python3 -m venv venv
fi

# Активация виртуального окружения и установка зависимостей
print_info "Установка зависимостей Python..."
source venv/bin/activate

# Обновление pip
pip install --upgrade pip

# Создание requirements.txt
cat > requirements.txt << EOF
requests>=2.31.0
python-dotenv>=1.0.0
EOF

# Установка зависимостей
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "Зависимости установлены успешно"
else
    print_error "Ошибка при установке зависимостей"
    exit 1
fi

deactivate

# Создание скрипта запуска
print_info "Создание скрипта запуска..."
cat > run.sh << 'EOF'
#!/bin/bash

# Скрипт запуска для Linux

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
EOF

chmod +x run.sh

# Создание ярлыка на рабочем столе (опционально)
if [ -d "$HOME/Desktop" ]; then
    print_info "Создание ярлыка на рабочем столе..."
    cat > "$HOME/Desktop/vk-music-player.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=VK Music Player
Comment=Консольный плеер для ВКонтакте
Exec=$PWD/run.sh
Icon=audio-headphones
Terminal=true
Categories=Audio;Music;Player;
EOF
    
    chmod +x "$HOME/Desktop/vk-music-player.desktop"
    print_success "Ярлык создан на рабочем столе"
fi

echo
echo "========================================"
echo "   УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!       "
echo "========================================"
echo
echo "Для запуска программы:"
echo "  ./run.sh"
echo
echo "Или дважды кликните по ярлыку на рабочем столе"
echo
echo "Перед первым запуском создайте файл vk_token.txt"
echo "с вашим токеном VK или введите его в программе"
echo