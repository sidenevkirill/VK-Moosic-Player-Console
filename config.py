import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Информация о программе
PROGRAM_INFO = {
    "name": "VK Moosic Player & Console",
    "version": "0.0.3",
    "author": "LisDevs",
    "description": "Программа для работы с музыкой ВК",
    "release_date": "2025",
    "features": [
        "🎵 Моя музыка",
        "👥 Музыка друзей", 
        "👥 Музыка групп",
        "📋 Мои плейлисты", 
        "🔍 Поиск музыки",
        "📻 Рекомендации и популярная музыка",
        "💾 Загрузка токена из файла",
        "⌨️ Ручной ввод токена",
    ]
}

# Цвета для консоли (ANSI коды)
class Colors:
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Фоны
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Стили
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'

# Константы
TOKEN_FILE = 'vk_token.txt'
VK_API_VERSION = '5.131'
KATE_USER_AGENT = "KateMobileAndroid/51.1-442 (Android 11; SDK 30; arm64-v8a; Samsung SM-G991B; ru_RU)"
POPULAR_QUERIES = [
    "популярные песни 2024", "хиты", "top hits", "новинки музыки",
    "русские хиты", "зарубежные хиты", "топ чарт", "billboard top 100"
]