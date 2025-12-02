import tempfile
import webbrowser
import subprocess
import sys
import os
import re
import shutil
from datetime import datetime
from config import Colors, PROGRAM_INFO
from ui import ConsoleUI

def play_audio(track_url, track_name, vk_manager, auto_download=False):
    """Воспроизвести аудиозапись с возможностью скачивания"""
    try:
        vk_manager.ui.print_playing(f"Воспроизведение: {track_name}")
        
        # Создаем временный файл
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_filename = temp_file.name
        temp_file.close()
        
        vk_manager.ui.print_downloading("Скачивание трека...")
        
        # Скачиваем трек
        headers = vk_manager.headers.copy()
        headers.update({
            'Referer': 'https://vk.com/',
            'Origin': 'https://vk.com'
        })
        
        try:
            import requests
            response = requests.get(track_url, stream=True, headers=headers)
            if response.status_code == 200:
                with open(temp_filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Воспроизводим
                if os.name == 'nt':
                    os.startfile(temp_filename)
                elif os.name == 'posix':
                    if sys.platform == 'darwin':
                        subprocess.run(['open', temp_filename])
                    else:
                        subprocess.run(['xdg-open', temp_filename])
                
                vk_manager.ui.print_success(f"Аудио открыто в медиаплеере: {track_name}")
                
                # Предлагаем сохранить
                if not auto_download:
                    save = vk_manager.ui.get_input("\nСохранить файл? (y/n): ").strip().lower()
                    if save == 'y':
                        save_track_with_name(track_name, temp_filename, vk_manager)
                
                return True
            else:
                vk_manager.ui.print_error(f"Ошибка при скачивании: {response.status_code}")
                return False
                
        except Exception as e:
            vk_manager.ui.print_error(f"Ошибка скачивания: {e}")
            return False
        
    except Exception as e:
        vk_manager.ui.print_error(f"Ошибка при воспроизведении аудио: {e}")
        return False

def save_track_with_name(track_name, source_path, vk_manager):
    """Сохранить трек с правильным именем"""
    try:
        # Очищаем имя файла
        def clean_filename(name):
            # Удаляем недопустимые символы
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                name = name.replace(char, '_')
            # Убираем лишние пробелы
            name = ' '.join(name.split())
            # Ограничиваем длину
            if len(name) > 200:
                name = name[:200]
            return name
        
        # Создаем папку для загрузок
        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)
        
        # Создаем имя файла
        safe_name = clean_filename(track_name)
        filepath = os.path.join(download_dir, f"{safe_name}.mp3")
        
        # Проверяем существование
        counter = 1
        original_filepath = filepath
        while os.path.exists(filepath):
            name, ext = os.path.splitext(original_filepath)
            filepath = f"{name}_{counter}{ext}"
            counter += 1
        
        # Копируем файл
        shutil.copy2(source_path, filepath)
        vk_manager.ui.print_success(f"Файл сохранен: {filepath}")
        
        # Удаляем временный файл
        try:
            os.unlink(source_path)
        except:
            pass
            
        return True
        
    except Exception as e:
        vk_manager.ui.print_error(f"Ошибка при сохранении: {e}")
        return False

def interactive_audio_player(audio_list, title, vk_manager):
    """Интерактивный плеер для прослушивания и скачивания аудиозаписей"""
    if not audio_list:
        vk_manager.ui.print_info("Нет аудиозаписей для воспроизведения")
        return
    
    current_track = None
    download_dir = "downloads"
    
    # Создаем директорию для загрузок
    os.makedirs(download_dir, exist_ok=True)
    
    vk_manager.ui.print_header(title)
    
    while True:
        print(f"\n{Colors.BRIGHT_CYAN}📊 Статистика:{Colors.RESET}")
        print(f"   {Colors.BRIGHT_WHITE}Доступно треков:{Colors.RESET} {Colors.BRIGHT_GREEN}{len(audio_list)}{Colors.RESET}")
        print(f"   {Colors.BRIGHT_WHITE}Папка загрузок:{Colors.RESET} {Colors.BRIGHT_BLUE}{download_dir}{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_CYAN}🎵 Список треков:{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}{'─' * 80}{Colors.RESET}")
        
        for i, track in enumerate(audio_list, 1):
            artist = track.get('artist', 'Unknown Artist')
            title_track = track.get('title', 'Unknown Title')
            duration = track.get('duration', 0)
            
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
            
            # Чередование цветов для строк
            if i % 2 == 0:
                color = Colors.BRIGHT_WHITE
            else:
                color = Colors.WHITE
            
            # Маркер для текущего трека
            marker = "▶ " if track == current_track else "  "
            
            print(f"{Colors.BRIGHT_YELLOW}{i:3d}.{Colors.RESET} {marker}{color}{artist} - {title_track} {Colors.BRIGHT_BLACK}({duration_str}){Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_CYAN}🎮 Управление:{Colors.RESET}")
        print(f"   {Colors.BRIGHT_YELLOW}[1-{len(audio_list)}]{Colors.RESET} - Выбрать трек")
        print(f"   {Colors.BRIGHT_YELLOW}p{Colors.RESET} - Воспроизвести текущий/случайный трек")
        print(f"   {Colors.BRIGHT_YELLOW}d[номер]{Colors.RESET} - Скачать трек (пример: d5)")
        print(f"   {Colors.BRIGHT_YELLOW}da{Colors.RESET} - Скачать все треки")
        print(f"   {Colors.BRIGHT_YELLOW}dir{Colors.RESET} - Изменить папку загрузки")
        print(f"   {Colors.BRIGHT_YELLOW}o{Colors.RESET} - Открыть папку загрузок")
        print(f"   {Colors.BRIGHT_YELLOW}q{Colors.RESET} - Выход в меню")
        
        choice = vk_manager.ui.get_input("\nВаш выбор: ").strip().lower()
        
        if choice == 'q':
            break
            
        elif choice == 'p':
            if current_track:
                # Воспроизвести текущий трек
                artist = current_track.get('artist', 'Unknown Artist')
                title_track = current_track.get('title', 'Unknown Title')
                track_url = current_track.get('url')
                
                if track_url:
                    track_name = f"{artist} - {title_track}"
                    play_audio(track_url, track_name, vk_manager)
                else:
                    vk_manager.ui.print_error("У этого трека нет ссылки для воспроизведения")
            else:
                # Воспроизвести случайный трек
                import random
                track = random.choice(audio_list)
                current_track = track
                artist = track.get('artist', 'Unknown Artist')
                title_track = track.get('title', 'Unknown Title')
                track_url = track.get('url')
                
                if track_url:
                    track_name = f"{artist} - {title_track}"
                    play_audio(track_url, track_name, vk_manager)
                else:
                    vk_manager.ui.print_error("У этого трека нет ссылки для воспроизведения")
                    
        elif choice.startswith('d'):
            if choice == 'da':
                # Скачать все треки
                vk_manager.ui.print_info(f"Начинаю скачивание всех {len(audio_list)} треков...")
                downloaded = 0
                failed = 0
                
                for i, track in enumerate(audio_list, 1):
                    artist = track.get('artist', 'Unknown Artist')
                    title_track = track.get('title', 'Unknown Title')
                    track_url = track.get('url')
                    
                    if track_url:
                        vk_manager.ui.print_info(f"[{i}/{len(audio_list)}] Скачиваю: {artist} - {title_track}")
                        
                        # Создаем временный файл
                        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                        temp_filename = temp_file.name
                        temp_file.close()
                        
                        # Скачиваем
                        try:
                            import requests
                            headers = vk_manager.headers.copy()
                            headers.update({
                                'Referer': 'https://vk.com/',
                                'Origin': 'https://vk.com'
                            })
                            
                            response = requests.get(track_url, stream=True, headers=headers)
                            if response.status_code == 200:
                                with open(temp_filename, 'wb') as f:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                
                                # Сохраняем с правильным именем
                                track_name = f"{artist} - {title_track}"
                                if save_track_with_name(track_name, temp_filename, vk_manager):
                                    downloaded += 1
                                else:
                                    failed += 1
                            else:
                                failed += 1
                                
                        except Exception as e:
                            vk_manager.ui.print_error(f"Ошибка при скачивании: {e}")
                            failed += 1
                    else:
                        failed += 1
                
                vk_manager.ui.print_success(f"Скачивание завершено!")
                vk_manager.ui.print_info(f"Успешно: {downloaded}, Не удалось: {failed}")
                
            elif len(choice) > 1:
                # Скачать конкретный трек
                try:
                    if choice[1:].isdigit():
                        track_index = int(choice[1:]) - 1
                        if 0 <= track_index < len(audio_list):
                            track = audio_list[track_index]
                            artist = track.get('artist', 'Unknown Artist')
                            title_track = track.get('title', 'Unknown Title')
                            track_url = track.get('url')
                            
                            if track_url:
                                vk_manager.ui.print_info(f"Скачиваю: {artist} - {title_track}")
                                
                                # Создаем временный файл
                                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                                temp_filename = temp_file.name
                                temp_file.close()
                                
                                # Скачиваем
                                try:
                                    import requests
                                    headers = vk_manager.headers.copy()
                                    headers.update({
                                        'Referer': 'https://vk.com/',
                                        'Origin': 'https://vk.com'
                                    })
                                    
                                    response = requests.get(track_url, stream=True, headers=headers)
                                    if response.status_code == 200:
                                        with open(temp_filename, 'wb') as f:
                                            for chunk in response.iter_content(chunk_size=8192):
                                                if chunk:
                                                    f.write(chunk)
                                        
                                        # Сохраняем с правильным именем
                                        track_name = f"{artist} - {title_track}"
                                        save_track_with_name(track_name, temp_filename, vk_manager)
                                    else:
                                        vk_manager.ui.print_error(f"Ошибка HTTP: {response.status_code}")
                                        
                                except Exception as e:
                                    vk_manager.ui.print_error(f"Ошибка при скачивании: {e}")
                            else:
                                vk_manager.ui.print_error("У трека нет ссылки для скачивания")
                        else:
                            vk_manager.ui.print_error("Неверный номер трека")
                    else:
                        vk_manager.ui.print_error("Неверный формат. Используйте: d[номер]")
                except ValueError:
                    vk_manager.ui.print_error("Неверный ввод")
                    
        elif choice == 'dir':
            new_dir = vk_manager.ui.get_input(f"Текущая папка: {download_dir}\nНовая папка: ").strip()
            if new_dir:
                download_dir = new_dir
                os.makedirs(download_dir, exist_ok=True)
                vk_manager.ui.print_success(f"Папка загрузок изменена на: {download_dir}")
                
        elif choice == 'o':
            # Открыть папку загрузок
            try:
                if os.name == 'nt':
                    os.startfile(download_dir)
                elif os.name == 'posix':
                    if sys.platform == 'darwin':
                        subprocess.run(['open', download_dir])
                    else:
                        subprocess.run(['xdg-open', download_dir])
                vk_manager.ui.print_success(f"Открыта папка: {download_dir}")
            except Exception as e:
                vk_manager.ui.print_error(f"Не удалось открыть папку: {e}")
                
        else:
            try:
                track_index = int(choice) - 1
                if 0 <= track_index < len(audio_list):
                    track = audio_list[track_index]
                    current_track = track
                    artist = track.get('artist', 'Unknown Artist')
                    title_track = track.get('title', 'Unknown Title')
                    track_url = track.get('url')
                    
                    if track_url:
                        # Сначала спрашиваем, что делать с треком
                        print(f"\n{Colors.BRIGHT_CYAN}🎵 Выбран трек: {artist} - {title_track}{Colors.RESET}")
                        print(f"{Colors.BRIGHT_CYAN}🎮 Действия:{Colors.RESET}")
                        print(f"   {Colors.BRIGHT_YELLOW}1{Colors.RESET} - Воспроизвести")
                        print(f"   {Colors.BRIGHT_YELLOW}2{Colors.RESET} - Скачать")
                        print(f"   {Colors.BRIGHT_YELLOW}3{Colors.RESET} - Воспроизвести и скачать")
                        print(f"   {Colors.BRIGHT_YELLOW}4{Colors.RESET} - Показать информацию")
                        print(f"   {Colors.BRIGHT_YELLOW}0{Colors.RESET} - Отмена")
                        
                        action = vk_manager.ui.get_input("\nВаш выбор: ").strip()
                        
                        if action == '1':
                            track_name = f"{artist} - {title_track}"
                            play_audio(track_url, track_name, vk_manager)
                        elif action == '2':
                            vk_manager.ui.print_info(f"Скачиваю: {artist} - {title_track}")
                            
                            # Создаем временный файл
                            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                            temp_filename = temp_file.name
                            temp_file.close()
                            
                            # Скачиваем
                            try:
                                import requests
                                headers = vk_manager.headers.copy()
                                headers.update({
                                    'Referer': 'https://vk.com/',
                                    'Origin': 'https://vk.com'
                                })
                                
                                response = requests.get(track_url, stream=True, headers=headers)
                                if response.status_code == 200:
                                    with open(temp_filename, 'wb') as f:
                                        for chunk in response.iter_content(chunk_size=8192):
                                            if chunk:
                                                f.write(chunk)
                                    
                                    # Сохраняем с правильным именем
                                    track_name = f"{artist} - {title_track}"
                                    save_track_with_name(track_name, temp_filename, vk_manager)
                                else:
                                    vk_manager.ui.print_error(f"Ошибка HTTP: {response.status_code}")
                                    
                            except Exception as e:
                                vk_manager.ui.print_error(f"Ошибка при скачивании: {e}")
                        elif action == '3':
                            track_name = f"{artist} - {title_track}"
                            play_audio(track_url, track_name, vk_manager, auto_download=True)
                        elif action == '4':
                            vk_manager.ui.clear_screen()
                            vk_manager.ui.print_header("ИНФОРМАЦИЯ О ТРЕКЕ")
                            
                            print(f"{Colors.BRIGHT_CYAN}🎵 Трек:{Colors.RESET}")
                            print(f"   {Colors.BRIGHT_WHITE}Исполнитель:{Colors.RESET} {artist}")
                            print(f"   {Colors.BRIGHT_WHITE}Название:{Colors.RESET} {title_track}")
                            print(f"   {Colors.BRIGHT_WHITE}Длительность:{Colors.RESET} {track.get('duration', 0)} сек.")
                            
                            if 'album' in track:
                                print(f"   {Colors.BRIGHT_WHITE}Альбом:{Colors.RESET} {track['album']}")
                            if 'genre' in track:
                                print(f"   {Colors.BRIGHT_WHITE}Жанр:{Colors.RESET} {track['genre']}")
                            if 'year' in track:
                                print(f"   {Colors.BRIGHT_WHITE}Год:{Colors.RESET} {track['year']}")
                            
                            vk_manager.ui.get_input("\nНажмите Enter чтобы продолжить...")
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
    ui.print_menu_item("11", "🔧 Диагностика плейлистов")
    ui.print_menu_item("12", "🚪 Выход")
    
    print(f"\n{Colors.BRIGHT_BLACK}{'─' * 60}{Colors.RESET}")
