import tempfile
import webbrowser
import subprocess
import sys
import os
from datetime import datetime
from config import Colors, PROGRAM_INFO
from ui import ConsoleUI

def play_audio(track_url, track_name, vk_manager):
    """Воспроизвести аудиозапись"""
    try:
        vk_manager.ui.print_playing(f"Воспроизведение: {track_name}")
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        vk_manager.ui.print_downloading("Скачивание трека...")
        if vk_manager.download_audio(track_url, temp_filename):
            try:
                if os.name == 'nt':
                    os.startfile(temp_filename)
                elif os.name == 'posix':
                    if sys.platform == 'darwin':
                        subprocess.run(['open', temp_filename])
                    else:
                        subprocess.run(['xdg-open', temp_filename])
                vk_manager.ui.print_success(f"Аудио открыто в медиаплеере: {track_name}")
                
            except Exception as e:
                vk_manager.ui.print_error(f"Не удалось открыть аудио автоматически: {e}")
                vk_manager.ui.print_info(f"Аудиофайл сохранен как: {temp_filename}")
        
        return True
        
    except Exception as e:
        vk_manager.ui.print_error(f"Ошибка при воспроизведении аудио: {e}")
        return False

def interactive_audio_player(audio_list, title, vk_manager):
    """Интерактивный плеер для прослушивания аудиозаписей"""
    if not audio_list:
        vk_manager.ui.print_info("Нет аудиозаписей для воспроизведения")
        return
    
    vk_manager.ui.print_header(title)
    
    while True:
        print(f"\n{Colors.BRIGHT_CYAN}📊 Статистика:{Colors.RESET}")
        print(f"   {Colors.BRIGHT_WHITE}Доступно треков:{Colors.RESET} {Colors.BRIGHT_GREEN}{len(audio_list)}{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_CYAN}🎵 Список треков:{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}{'─' * 80}{Colors.RESET}")
        
        for i, track in enumerate(audio_list, 1):
            artist = track.get('artist', 'Unknown Artist')
            title = track.get('title', 'Unknown Title')
            duration = track.get('duration', 0)
            
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
            
            # Чередование цветов для строк
            if i % 2 == 0:
                color = Colors.BRIGHT_WHITE
            else:
                color = Colors.WHITE
            
            print(f"{Colors.BRIGHT_YELLOW}{i:3d}.{Colors.RESET} {color}{artist} - {title} {Colors.BRIGHT_BLACK}({duration_str}){Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_CYAN}🎮 Управление:{Colors.RESET}")
        print(f"   {Colors.BRIGHT_YELLOW}[1-{len(audio_list)}]{Colors.RESET} - Выбрать трек для прослушивания")
        print(f"   {Colors.BRIGHT_YELLOW}q{Colors.RESET} - Выход в меню")
        print(f"   {Colors.BRIGHT_YELLOW}p{Colors.RESET} - Воспроизвести случайный трек")
        
        choice = vk_manager.ui.get_input("\nВаш выбор: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'p':
            import random
            track = random.choice(audio_list)
            artist = track.get('artist', 'Unknown Artist')
            title = track.get('title', 'Unknown Title')
            track_url = track.get('url')
            
            if track_url:
                track_name = f"{artist} - {title}"
                play_audio(track_url, track_name, vk_manager)
            else:
                vk_manager.ui.print_error("У этого трека нет ссылки для воспроизведения")
        else:
            try:
                track_index = int(choice) - 1
                if 0 <= track_index < len(audio_list):
                    track = audio_list[track_index]
                    artist = track.get('artist', 'Unknown Artist')
                    title = track.get('title', 'Unknown Title')
                    track_url = track.get('url')
                    
                    if track_url:
                        track_name = f"{artist} - {title}"
                        play_audio(track_url, track_name, vk_manager)
                    else:
                        vk_manager.ui.print_error("У этого трека нет ссылки для воспроизведения")
                else:
                    vk_manager.ui.print_error("Неверный номер трека")
            except ValueError:
                vk_manager.ui.print_error("Неверный ввод")

def show_program_info():
    """Показать информацию о программе"""
    ui = ConsoleUI()
    ui.clear_screen()
    
    # ASCII арт
    ascii_art = """
    ╔═══════════════════════════════════════════════════════╗
    ║  ██╗   ██╗  ██╗  ██╗  ████╗   ████╗  ██████╗         ║
    ║  ██║   ██║  ██║ ██╔╝  ████╗ ██████║  ██╔══██╗        ║
    ║  ██║   ██║  █████╔╝   ██╔████╔████║  ██████╔╝        ║
    ║  ╚██╗ ██╔╝  ██╔═██╗   ██║╚██╔╝████║  ██╔═══╝         ║
    ║   ╚████╔╝   ██║  ██╗  ██║ ╚═╝ ████║  ██║             ║
    ║    ╚═══╝    ╚═╝  ╚═╝  ╚═╝     ╚═══╝  ╚═╝             ║
    ║                                                       ║
    ║        VK Music Player • Console PC              ║
    ╚═══════════════════════════════════════════════════════╝
    """
    
    print(f"{Colors.BRIGHT_CYAN}{ascii_art}{Colors.RESET}")
    
    info_box = f"""
    Название: {PROGRAM_INFO['name']}
    Версия: {PROGRAM_INFO['version']}
    Автор: {PROGRAM_INFO['author']}
    Год выпуска: {PROGRAM_INFO['release_date']}
    Описание: {PROGRAM_INFO['description']}
    
    Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Python: {sys.version.split()[0]}
    Платформа: {sys.platform}
    """
    
    ui.print_box(info_box, "ИНФОРМАЦИЯ О ПРОГРАММЕ")
    
    print(f"\n{Colors.BRIGHT_CYAN}✨ Возможности:{Colors.RESET}")
    for i, feature in enumerate(PROGRAM_INFO['features'], 1):
        if i % 2 == 0:
            color = Colors.BRIGHT_WHITE
        else:
            color = Colors.WHITE
        print(f"   {color}{feature}{Colors.RESET}")

def show_auth_help():
    """Показать инструкцию по получению токена"""
    ui = ConsoleUI()
    ui.clear_screen()
    
    ui.print_header("ИНСТРУКЦИЯ ПО ПОЛУЧЕНИЮ VK ТОКЕНА")
    
    instructions = """
    1. Откройте браузер и перейдите по ссылке:
    
    2. Авторизуйтесь в VK
    
    3. Скопируйте токен из адресной строки 
       (параметр access_token между access_token= и &expires_in)
    
    4. Вставьте токен в программу
    
    Пример токена: vk1.a.long_string_of_characters_here
    
    Важно: Никому не передавайте ваш токен!
    """
    
    ui.print_box(instructions, "ШАГИ ДЛЯ ПОЛУЧЕНИЯ ТОКЕНА", Colors.BRIGHT_YELLOW)
    
    print(f"\n{Colors.BRIGHT_CYAN}🔗 Ссылка для получения токена:{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLUE}https://oauth.vk.com/authorize?client_id=2685278&scope=1073737727&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1{Colors.RESET}")
    
    open_browser = ui.get_input("\nОткрыть ссылку в браузере? (y/n): ").strip().lower()
    if open_browser == 'y':
        webbrowser.open("https://oauth.vk.com/authorize?client_id=2685278&scope=1073737727&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1")
        ui.print_success("Браузер открыт!")

def show_main_menu():
    """Показать главное меню"""
    ui = ConsoleUI()
    
    # ASCII заголовок меню
    menu_header = """
    ╔═══════════════════════════════════════════════════════╗
    ║                    ГЛАВНОЕ МЕНЮ                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    
    print(f"{Colors.BRIGHT_CYAN}{menu_header}{Colors.RESET}")
    
    # Группировка пунктов меню
    print(f"{Colors.BRIGHT_MAGENTA}🔐 АВТОРИЗАЦИЯ:{Colors.RESET}")
    ui.print_menu_item("1", "📁 Загрузить токен из файла vk_token.txt")
    ui.print_menu_item("2", "📝 Ввести токен вручную")
    ui.print_menu_item("3", "📖 Инструкция по получению токена")
    
    print(f"\n{Colors.BRIGHT_GREEN}🎵 МУЗЫКА:{Colors.RESET}")
    ui.print_menu_item("4", "🎵 Моя музыкa")
    ui.print_menu_item("5", "👥 Музыка друзей")
    ui.print_menu_item("6", "📋 Мои плейлисты")
    ui.print_menu_item("7", "📻 Рекомендации")
    ui.print_menu_item("8", "🔎 Поиск треков")
    
    print(f"\n{Colors.BRIGHT_YELLOW}⚙️  СИСТЕМА:{Colors.RESET}")
    ui.print_menu_item("9", "💡 Информация о API")
    ui.print_menu_item("10", "📝 О программе")
    ui.print_menu_item("11", "🚪 Выход")
    
    print(f"\n{Colors.BRIGHT_BLACK}{'─' * 60}{Colors.RESET}")