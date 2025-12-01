#!/usr/bin/env python3
"""
VK Music Player - Console Edition
Главный файл запуска программы
"""

import logging
import sys
import traceback
from config import Colors, PROGRAM_INFO
from ui import ConsoleUI
from vk_api import VKMusicManager
from utils import (
    show_program_info, 
    show_auth_help, 
    show_main_menu,
    interactive_audio_player,
    play_audio
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def friends_music_interactive(vk_manager):
    """Интерактивное прослушивание музыки друзей"""
    if not vk_manager.token:
        vk_manager.ui.print_error("Токен не установлен")
        return
    
    vk_manager.ui.print_header("МУЗЫКА ДРУЗЕЙ")
    
    # Получаем список друзей
    vk_manager.ui.print_info("Загрузка списка друзей...")
    friends_result = vk_manager.get_friends_list()
    
    if not friends_result.get("success"):
        vk_manager.ui.print_error(f"Не удалось получить список друзей: {friends_result.get('error')}")
        return
    
    friends = friends_result["friends"]
    
    if not friends:
        vk_manager.ui.print_info("У вас нет друзей или доступ к списку друзей ограничен")
        return
    
    while True:
        print(f"\n{Colors.BRIGHT_CYAN}👥 Список друзей:{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}{'─' * 80}{Colors.RESET}")
        
        for i, friend in enumerate(friends, 1):
            first_name = friend.get('first_name', '')
            last_name = friend.get('last_name', '')
            
            if i % 2 == 0:
                color = Colors.BRIGHT_WHITE
            else:
                color = Colors.WHITE
            
            print(f"{Colors.BRIGHT_YELLOW}{i:3d}.{Colors.RESET} {color}{first_name} {last_name}{Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_CYAN}🎮 Управление:{Colors.RESET}")
        print(f"   {Colors.BRIGHT_YELLOW}[1-{len(friends)}]{Colors.RESET} - Выбрать друга для просмотра музыки")
        print(f"   {Colors.BRIGHT_YELLOW}q{Colors.RESET} - Выход в меню")
        print(f"   {Colors.BRIGHT_YELLOW}r{Colors.RESET} - Случайный друг")
        
        choice = vk_manager.ui.get_input("\nВаш выбор: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'r':
            import random
            friend = random.choice(friends)
            friend_id = friend.get('id')
            first_name = friend.get('first_name', '')
            last_name = friend.get('last_name', '')
            friend_name = f"{first_name} {last_name}"
            
            vk_manager.ui.print_info(f"Загружаем музыку случайного друга: {friend_name}")
            audio_result = vk_manager.get_friend_audio_list(friend_id)
            
            if audio_result.get("success"):
                audio_list = audio_result["audio_list"]
                if audio_list:
                    interactive_audio_player(audio_list, f"МУЗЫКА ДРУГА: {friend_name}", vk_manager)
                else:
                    vk_manager.ui.print_info(f"У {friend_name} нет аудиозаписей или доступ ограничен")
            else:
                vk_manager.ui.print_error(f"Не удалось загрузить музыку: {audio_result.get('error')}")
        else:
            try:
                friend_index = int(choice) - 1
                if 0 <= friend_index < len(friends):
                    friend = friends[friend_index]
                    friend_id = friend.get('id')
                    first_name = friend.get('first_name', '')
                    last_name = friend.get('last_name', '')
                    friend_name = f"{first_name} {last_name}"
                    
                    vk_manager.ui.print_info(f"Загружаем музыку друга: {friend_name}")
                    audio_result = vk_manager.get_friend_audio_list(friend_id)
                    
                    if audio_result.get("success"):
                        audio_list = audio_result["audio_list"]
                        if audio_list:
                            interactive_audio_player(audio_list, f"МУЗЫКА ДРУГА: {friend_name}", vk_manager)
                        else:
                            vk_manager.ui.print_info(f"У {friend_name} нет аудиозаписей или доступ ограничен")
                    else:
                        vk_manager.ui.print_error(f"Не удалось загрузить музыку: {audio_result.get('error')}")
                else:
                    vk_manager.ui.print_error("Неверный номер друга")
            except ValueError:
                vk_manager.ui.print_error("Неверный ввод")

def playlists_interactive(vk_manager):
    """Интерактивное управление плейлистами"""
    if not vk_manager.token or not vk_manager.user_id:
        vk_manager.ui.print_error("Токен не установлен или user_id не определен")
        return
    
    vk_manager.ui.print_header("МОИ ПЛЕЙЛИСТЫ")
    
    vk_manager.ui.print_info("Загрузка плейлистов...")
    playlists_result = vk_manager.get_playlists()
    
    if not playlists_result.get("success"):
        vk_manager.ui.print_error(f"Не удалось получить список плейлистов: {playlists_result.get('error')}")
        return
    
    playlists = playlists_result["playlists"]
    
    if not playlists:
        vk_manager.ui.print_info("У вас нет плейлистов")
        return
    
    while True:
        print(f"\n{Colors.BRIGHT_CYAN}📋 Список плейлистов:{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}{'─' * 80}{Colors.RESET}")
        
        for i, playlist in enumerate(playlists, 1):
            title = playlist.get('title', 'Без названия')
            count = playlist.get('count', 0)
            
            if i % 2 == 0:
                color = Colors.BRIGHT_WHITE
            else:
                color = Colors.WHITE
            
            print(f"{Colors.BRIGHT_YELLOW}{i:3d}.{Colors.RESET} {color}{title} {Colors.BRIGHT_BLACK}({count} треков){Colors.RESET}")
        
        print(f"\n{Colors.BRIGHT_CYAN}🎮 Управление:{Colors.RESET}")
        print(f"   {Colors.BRIGHT_YELLOW}[1-{len(playlists)}]{Colors.RESET} - Выбрать плейлист")
        print(f"   {Colors.BRIGHT_YELLOW}q{Colors.RESET} - Выход в меню")
        
        choice = vk_manager.ui.get_input("\nВаш выбор: ").strip().lower()
        
        if choice == 'q':
            break
        else:
            try:
                playlist_index = int(choice) - 1
                if 0 <= playlist_index < len(playlists):
                    playlist = playlists[playlist_index]
                    playlist_id = playlist.get('id')
                    playlist_title = playlist.get('title', 'Без названия')
                    
                    vk_manager.ui.print_info(f"Загружаем плейлист: {playlist_title}")
                    tracks_result = vk_manager.get_playlist_tracks(playlist_id)
                    
                    if tracks_result.get("success"):
                        audio_list = tracks_result["audio_list"]
                        if audio_list:
                            interactive_audio_player(audio_list, f"ПЛЕЙЛИСТ: {playlist_title}", vk_manager)
                        else:
                            vk_manager.ui.print_info("В плейлисте нет треков")
                    else:
                        vk_manager.ui.print_error(f"Не удалось загрузить треки: {tracks_result.get('error')}")
                else:
                    vk_manager.ui.print_error("Неверный номер плейлиста")
            except ValueError:
                vk_manager.ui.print_error("Неверный ввод")

def search_tracks_interactive(vk_manager):
    """Интерактивный поиск треков"""
    if not vk_manager.token:
        vk_manager.ui.print_error("Токен не установлен")
        return
    
    vk_manager.ui.print_header("ПОИСК ТРЕКОВ")
    
    while True:
        query = vk_manager.ui.get_input("Введите запрос для поиска (или 'q' для выхода): ").strip()
        
        if query.lower() == 'q':
            break
            
        if not query:
            vk_manager.ui.print_error("Запрос не может быть пустым")
            continue
        
        vk_manager.ui.print_info(f"Ищем: {query}")
        
        result = vk_manager.search_audio(query)
        if not result["success"]:
            vk_manager.ui.print_error(f"Ошибка поиска: {result.get('error')}")
            continue
        
        audio_list = result["results"]
        
        if not audio_list:
            vk_manager.ui.print_info("По вашему запросу ничего не найдено")
            continue
        
        vk_manager.ui.print_success(f"Найдено результатов: {len(audio_list)}")
        interactive_audio_player(audio_list, "РЕЗУЛЬТАТЫ ПОИСКА", vk_manager)

def get_recommendations_info(vk_manager):
    """Рекомендации по использованию VK API"""
    recommendations = []
    
    if not vk_manager.token:
        recommendations.append("❌ Токен не установлен")
        return recommendations
    
    validity = vk_manager.check_token_validity()
    if not validity["valid"]:
        recommendations.append(f"❌ Токен невалиден: {validity.get('error_msg')}")
        return recommendations        
    
    available_methods = []
    unavailable_methods = []
    
    test_methods = [
        ("friends.get", "Друзья"),
        ("audio.get", "Аудиозаписи"),
        ("audio.getPlaylists", "Плейлисты"),
        ("audio.getRecommendations", "Рекомендации"),
        ("audio.search", "Поиск музыки"),
        ("gifts.get", "Подарки"),
        ("messages.getConversations", "Сообщения"),
        ("photos.get", "Фотографии")
    ]
    
    for method, description in test_methods:
        url = f"https://api.vk.com/method/{method}"
        params = {
            "access_token": vk_manager.token,
            "v": "5.131",
            "count": 1
        }
        
        try:
            response = requests.get(url, params=params, headers=vk_manager.headers)
            data = response.json()
            
            if "response" in data:
                available_methods.append(description)
            else:
                error_code = data.get("error", {}).get("error_code", 0)
                if error_code == 15:
                    unavailable_methods.append(f"{description} (нет доступа)")
                else:
                    unavailable_methods.append(f"{description} (ошибка: {error_code})")
                    
        except Exception:
            unavailable_methods.append(f"{description} (ошибка запроса)")
    
    recommendations.append("✅ Токен валиден и работает")
    recommendations.append(f"👤 Пользователь: {validity['user_info'].get('first_name', '')} {validity['user_info'].get('last_name', '')}")
    
    if available_methods:
        recommendations.append("✅ Доступные методы:")
        for method in available_methods:
            recommendations.append(f"   • {method}")
    
    if unavailable_methods:
        recommendations.append("❌ Недоступные методы:")
        for method in unavailable_methods:
            recommendations.append(f"   • {method}")
    
    recommendations.append("\n💡 Рекомендации:")
    
    if "Друзья" in [m for m in unavailable_methods if "Друзья" in m]:
        recommendations.append("   • Для доступа к друзьям нужны права: friends")
    
    if "Аудиозаписи" in [m for m in unavailable_methods if "Аудиозаписи" in m]:
        recommendations.append("   • Для доступа к аудио нужны права: audio")
    
    if "Плейлисты" in [m for m in unavailable_methods if "Плейлисты" in m]:
        recommendations.append("   • Для доступа к плейлистам нужны права: audio")
    
    if "Рекомендации" in [m for m in unavailable_methods if "Рекомендации" in m]:
        recommendations.append("   • Для доступа к рекомендации нужны права: audio")
    
    if "Поиск музыки" in [m for m in unavailable_methods if "Поиск музыки" in m]:
        recommendations.append("   • Для доступа к поиску нужны права: audio")
    
    if "Аудиозаписи" in [m for m in available_methods if "Аудиозаписи" in m]:
        recommendations.append("   • Доступен интерактивный аудиоплеер")
    
    if "Друзья" in [m for m in available_methods if "Друзья" in m]:
        recommendations.append("   • Доступна музыка друзей")
    
    if "Плейлисты" in [m for m in available_methods if "Плейлисты" in m]:
        recommendations.append("   • Доступно управление плейлистами")
    
    if "Поиск музыки" in [m for m in available_methods if "Поиск музыки" in m]:
        recommendations.append("   • Доступен поиск музыки")
    
    if "Рекомендации" in [m for m in available_methods if "Рекомендации" in m]:
        recommendations.append("   • Доступны персонализированные рекомендации")
    else:
        recommendations.append("   • Рекомендации будут показаны через популярную музыку")
    
    return recommendations

def main():
    """Основная функция"""
    ui = ConsoleUI()
    ui.clear_screen()
    
    # Приветственный экран
    welcome_art = f"""
    {Colors.BRIGHT_CYAN}╔═══════════════════════════════════════════════════════╗{Colors.RESET}
    {Colors.BRIGHT_CYAN}║                                                       ║{Colors.RESET}
    {Colors.BRIGHT_CYAN}║    {Colors.BRIGHT_MAGENTA}Добро пожаловать в VK-Moosic-Player-Console!       {Colors.BRIGHT_CYAN}║{Colors.RESET}
    {Colors.BRIGHT_CYAN}║                                                       ║{Colors.RESET}
    {Colors.BRIGHT_CYAN}║    Версия: {PROGRAM_INFO['version']}                                      ║{Colors.RESET}
    {Colors.BRIGHT_CYAN}║    Автор: {PROGRAM_INFO['author']}                                     ║{Colors.RESET}
    {Colors.BRIGHT_CYAN}║                                                       ║{Colors.RESET}
    {Colors.BRIGHT_CYAN}╚═══════════════════════════════════════════════════════╝{Colors.RESET}
    """
    
    print(welcome_art)
    print(f"\n{Colors.BRIGHT_BLACK}Нажмите Enter для продолжения...{Colors.RESET}")
    input()
    
    vk_manager = VKMusicManager(ui)
    
    while True:
        ui.clear_screen()
        show_main_menu()
        
        choice = ui.get_input("\nВаш выбор (1-11): ").strip()
        
        if choice == "1":
            ui.clear_screen()
            ui.print_header("ЗАГРУЗКА ТОКЕНА ИЗ ФАЙЛА")
            if vk_manager.load_token_from_file():
                validity = vk_manager.check_token_validity()
                if validity["valid"]:
                    ui.print_success(f"Токен валиден! Добро пожаловать, {validity['user_info'].get('first_name', '')}!")
                else:
                    ui.print_error(f"Токен невалиден: {validity.get('error_msg')}")
            ui.get_input("\nНажмите Enter чтобы продолжить...")
            
        elif choice == "2":
            ui.clear_screen()
            if vk_manager.input_token_manually():
                validity = vk_manager.check_token_validity()
                if validity["valid"]:
                    ui.print_success(f"Токен установлен! Добро пожаловать, {validity['user_info'].get('first_name', '')}!")
            ui.get_input("\nНажмите Enter чтобы продолжить...")
            
        elif choice == "3":
            show_auth_help()
            ui.get_input("\nНажмите Enter чтобы продолжить...")
            
        elif choice == "4":
            if not vk_manager.token:
                ui.print_error("Токен не загружен. Сначала загрузите токен (пункт 1 или 2)")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
                
            validity = vk_manager.check_token_validity()
            if not validity["valid"]:
                ui.print_error(f"Токен невалиден: {validity.get('error_msg')}")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
            
            audio_result = vk_manager.get_my_audio_list()
            if audio_result.get("success"):
                interactive_audio_player(audio_result["audio_list"], "МОЯ МУЗЫКА", vk_manager)
            else:
                ui.print_error(f"Не удалось загрузить музыку: {audio_result.get('error')}")
                
        elif choice == "5":
            if not vk_manager.token:
                ui.print_error("Токен не загрушен. Сначала загрузите токен (пункт 1 или 2)")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
                
            validity = vk_manager.check_token_validity()
            if not validity["valid"]:
                ui.print_error(f"Токен невалиден: {validity.get('error_msg')}")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
            
            friends_music_interactive(vk_manager)
                
        elif choice == "6":
            if not vk_manager.token:
                ui.print_error("Токен не загружен. Сначала загрузите токен (пункт 1 или 2)")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
                
            validity = vk_manager.check_token_validity()
            if not validity["valid"]:
                ui.print_error(f"Токен невалиден: {validity.get('error_msg')}")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
            
            playlists_interactive(vk_manager)
                
        elif choice == "7":
            if not vk_manager.token:
                ui.print_error("Токен не загружен. Сначала загрузите токен (пункт 1 или 2)")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
                
            validity = vk_manager.check_token_validity()
            if not validity["valid"]:
                ui.print_error(f"Токен невалиден: {validity.get('error_msg')}")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
            
            audio_result = vk_manager.get_recommendations()
            if audio_result.get("success"):
                interactive_audio_player(audio_result["audio_list"], "РЕКОМЕНДАЦИИ", vk_manager)
            else:
                ui.print_error(f"Не удалось загрузить рекомендации: {audio_result.get('error')}")
                
        elif choice == "8":
            if not vk_manager.token:
                ui.print_error("Токен не загружен. Сначала загрузите токен (пункт 1 или 2)")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
                
            validity = vk_manager.check_token_validity()
            if not validity["valid"]:
                ui.print_error(f"Токен невалиден: {validity.get('error_msg')}")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
            
            search_tracks_interactive(vk_manager)
                
        elif choice == "9":
            if not vk_manager.token:
                ui.print_error("Токен не загружен. Сначала загрузите токен (пункт 1 или 2)")
                ui.get_input("\nНажмите Enter чтобы продолжить...")
                continue
                
            recommendations = get_recommendations_info(vk_manager)
            ui.clear_screen()
            ui.print_header("ИНФОРМАЦИЯ О VK API")
            
            for rec in recommendations:
                if rec.startswith("✅"):
                    print(f"{Colors.BRIGHT_GREEN}{rec}{Colors.RESET}")
                elif rec.startswith("❌"):
                    print(f"{Colors.BRIGHT_RED}{rec}{Colors.RESET}")
                elif rec.startswith("👤"):
                    print(f"{Colors.BRIGHT_CYAN}{rec}{Colors.RESET}")
                elif rec.startswith("💡"):
                    print(f"{Colors.BRIGHT_YELLOW}{rec}{Colors.RESET}")
                elif "•" in rec:
                    if "Доступные" in rec or "Недоступные" in rec:
                        print(f"{Colors.BRIGHT_WHITE}{rec}{Colors.RESET}")
                    elif "(нет доступа)" in rec:
                        print(f"{Colors.BRIGHT_RED}{rec}{Colors.RESET}")
                    else:
                        print(f"{Colors.WHITE}{rec}{Colors.RESET}")
                else:
                    print(f"{Colors.WHITE}{rec}{Colors.RESET}")
                    
            ui.get_input("\nНажмите Enter чтобы продолжить...")
                
        elif choice == "10":
            show_program_info()
            ui.get_input("\nНажмите Enter чтобы продолжить...")
                
        elif choice == "11":
            ui.clear_screen()
            goodbye_art = f"""
            {Colors.BRIGHT_CYAN}╔═══════════════════════════════════════════════════════╗{Colors.RESET}
            {Colors.BRIGHT_CYAN}║                                                       ║{Colors.RESET}
            {Colors.BRIGHT_CYAN}║    {Colors.BRIGHT_MAGENTA}    Спасибо за использование программы!           {Colors.BRIGHT_CYAN}║{Colors.RESET}
            {Colors.BRIGHT_CYAN}║                                                       ║{Colors.RESET}
            {Colors.BRIGHT_CYAN}║         {Colors.BRIGHT_GREEN}До новых встреч в мире музыки!{Colors.BRIGHT_CYAN}               ║{Colors.RESET}
            {Colors.BRIGHT_CYAN}║                                                       ║{Colors.RESET}
            {Colors.BRIGHT_CYAN}╚═══════════════════════════════════════════════════════╝{Colors.RESET}
            """
            print(goodbye_art)
            break
            
        else:
            ui.print_error("Неверный выбор")
            ui.get_input("\nНажмите Enter чтобы продолжить...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BRIGHT_YELLOW}👋 Программа прервана пользователем{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}❌ Критическая ошибка: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n{Colors.BRIGHT_BLACK}Нажмите Enter для выхода...{Colors.RESET}")
        input()