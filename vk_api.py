import requests
import logging
import os
import json
import shutil
import tempfile
from config import Colors, KATE_USER_AGENT, VK_API_VERSION, TOKEN_FILE, POPULAR_QUERIES

logger = logging.getLogger(__name__)

class VKMusicManager:
    def __init__(self, ui):
        self.token = None
        self.user_id = None
        self.user_info = None
        self.ui = ui
        
        self.headers = {
            'User-Agent': KATE_USER_AGENT,
            'Accept': 'application/json',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive'
        }

    def set_token(self, token):
        """Установить токен"""
        self.token = token
        if token and '.' in token:
            parts = token.split('.')
            if len(parts) > 0:
                try:
                    self.user_id = int(parts[0])
                except ValueError:
                    self.user_id = None
        else:
            self.user_id = None

    def load_token_from_file(self, filename=None):
        """Загрузить токен из файла"""
        if filename is None:
            filename = TOKEN_FILE
        
        try:
            # Ищем файл в нескольких возможных местах
            possible_paths = [
                filename,  # Текущая директория
                os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),  # Рядом с vk_api.py
                os.path.join(os.getcwd(), filename),  # Текущая рабочая директория
                os.path.expanduser(f"~/{filename}"),  # Домашняя директория
                os.path.expanduser(f"~/.config/{filename}"),  # Конфигурационная директория
            ]
            
            found_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    found_path = path
                    break
            
            if found_path:
                with open(found_path, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
                    if token:
                        self.set_token(token)
                        self.ui.print_success(f"Токен загружен из файла: {found_path}")
                        return True
                    else:
                        self.ui.print_error(f"Файл {found_path} пуст")
                        return False
            else:
                # Создаем пример файла с инструкцией
                example_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
                self.ui.print_error(f"Файл {filename} не найден!")
                self.ui.print_info("Искали в следующих местах:")
                for path in possible_paths:
                    self.ui.print_info(f"  - {path}")
                
                # Предлагаем создать пример файла
                create_example = self.ui.get_input("\nСоздать пример файла с инструкцией? (y/n): ").strip().lower()
                if create_example == 'y':
                    with open(example_file, 'w', encoding='utf-8') as f:
                        f.write("# Вставьте ваш VK токен на следующей строке\n")
                        f.write("# Пример токена: vk1.a.ABC123def456...\n")
                        f.write("# Получить токен можно через меню программы (пункт 3)\n")
                        f.write("\nВАШ_ТОКЕН_ЗДЕСЬ\n")
                    self.ui.print_success(f"Пример файла создан: {example_file}")
                    self.ui.print_info("Откройте этот файл и вставьте ваш токен вместо 'ВАШ_ТОКЕН_ЗДЕСЬ'")
                
                return False
        except Exception as e:
            self.ui.print_error(f"Ошибка при чтении файла: {e}")
            return False

    def save_token_to_file(self, filename=None):
        """Сохранить токен в файл"""
        if filename is None:
            filename = TOKEN_FILE
        
        if not self.token:
            self.ui.print_error("Нет токена для сохранения")
            return False
        
        try:
            # Сохраняем в несколько мест для удобства
            save_paths = [
                os.path.join(os.getcwd(), filename),  # Текущая рабочая директория
                os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),  # Рядом с vk_api.py
                os.path.expanduser(f"~/{filename}"),  # Домашняя директория
            ]
            
            success_count = 0
            for filepath in save_paths:
                try:
                    # Создаем директорию, если её нет
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(self.token)
                    
                    if success_count == 0:  # Первый успешный путь
                        self.ui.print_success(f"Токен сохранен в: {filepath}")
                    else:
                        self.ui.print_info(f"Также сохранен в: {filepath}")
                    
                    success_count += 1
                    
                except Exception as e:
                    self.ui.print_warning(f"Не удалось сохранить в {filepath}: {e}")
            
            if success_count > 0:
                return True
            else:
                self.ui.print_error("Не удалось сохранить токен ни в одном месте")
                return False
                
        except Exception as e:
            self.ui.print_error(f"Ошибка при сохранении токена: {e}")
            return False

    def input_token_manually(self):
        """Ввод токена вручную"""
        self.ui.print_header("РУЧНОЙ ВВОД ТОКЕНА")
        
        token = self.ui.get_input("Введите ваш VK токен: ").strip()
        
        if not token:
            self.ui.print_error("Токен не может быть пустым")
            return False
        
        # Проверяем токен сразу
        old_token = self.token
        old_user_id = self.user_id
        self.set_token(token)
        
        validity = self.check_token_validity()
        if not validity["valid"]:
            self.ui.print_error(f"Токен невалиден: {validity.get('error_msg')}")
            self.token = old_token  # Восстанавливаем старый токен
            self.user_id = old_user_id
            return False
        
        self.ui.print_success("Токен валиден!")
        
        # Показываем информацию о пользователе
        if self.user_info:
            first_name = self.user_info.get('first_name', '')
            last_name = self.user_info.get('last_name', '')
            self.ui.print_info(f"Вы авторизованы как: {first_name} {last_name} (ID: {self.user_id})")
        
        # Предлагаем сохранить токен
        save = self.ui.get_input("Сохранить токен в файл для будущего использования? (y/n): ").strip().lower()
        if save == 'y':
            self.save_token_to_file()
        
        return True

    def check_token_validity(self):
        """Проверить валидность токена"""
        if not self.token:
            return {"valid": False, "error_msg": "Токен не установлен"}
        
        url = "https://api.vk.com/method/users.get"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "fields": "first_name,last_name,photo_200"
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                self.user_info = data["response"][0]
                # Обновляем user_id из ответа API
                self.user_id = self.user_info.get('id')
                return {"valid": True, "user_info": self.user_info}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                error_code = data.get("error", {}).get("error_code", 0)
                
                if error_code == 5:
                    error_msg = "Токен недействителен (ошибка 5: Invalid token)"
                elif error_code == 10:
                    error_msg = "Внутренняя ошибка сервера (ошибка 10)"
                elif error_code == 28:
                    error_msg = "Превышено количество запросов (ошибка 28)"
                
                return {"valid": False, "error_msg": error_msg}
                
        except requests.exceptions.ConnectionError:
            return {"valid": False, "error_msg": "Нет подключения к интернету"}
        except requests.exceptions.Timeout:
            return {"valid": False, "error_msg": "Таймаут при подключении к VK"}
        except Exception as e:
            return {"valid": False, "error_msg": f"Ошибка запроса: {e}"}

    def get_friends_list(self):
        """Получить список друзей"""
        if not self.token or not self.user_id:
            return {"success": False, "error": "Токен не установлен или user_id не определен"}
        
        url = "https://api.vk.com/method/friends.get"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "count": 100,
            "fields": "first_name,last_name,photo_100",
            "order": "name"
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "friends": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_friend_audio_list(self, friend_id):
        """Получить список аудиозаписей друга"""
        if not self.token:
            return {"success": False, "error": "Токен не установлен"}
        
        url = "https://api.vk.com/method/audio.get"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "count": 100,
            "owner_id": friend_id
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "audio_list": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_my_audio_list(self):
        """Получить список моих аудиозаписей"""
        if not self.token or not self.user_id:
            return {"success": False, "error": "Токен не установлен или user_id не определен"}
        
        url = "https://api.vk.com/method/audio.get"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "count": 100,
            "owner_id": self.user_id
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "audio_list": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_playlists(self):
        """Получить список плейлистов"""
        if not self.token or not self.user_id:
            return {"success": False, "error": "Токен не установлен или user_id не определен"}
        
        url = "https://api.vk.com/method/audio.getPlaylists"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "owner_id": self.user_id,
            "count": 50,
            "extended": 1
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                items = data["response"]["items"]
                
                # Форматируем данные плейлистов
                playlists = []
                for item in items:
                    playlist = {
                        'id': item.get('id'),
                        'owner_id': item.get('owner_id'),
                        'title': item.get('title', 'Без названия'),
                        'description': item.get('description', ''),
                        'count': item.get('count', 0),
                        'followers': item.get('followers', 0),
                        'plays': item.get('plays', 0),
                        'photo': item.get('photo', {}),
                        'access_key': item.get('access_key', '')
                    }
                    playlists.append(playlist)
                
                return {"success": True, "playlists": playlists}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                self.ui.print_warning(f"Не удалось получить плейлисты: {error_msg}")
                
                # Возвращаем пустой список, если плейлистов нет
                return {"success": True, "playlists": []}
                
        except Exception as e:
            self.ui.print_error(f"Ошибка при получении плейлистов: {e}")
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_playlist_tracks(self, playlist_id, owner_id=None, access_key=None):
        """Получить треки из плейлиста - ИСПРАВЛЕННЫЙ МЕТОД"""
        if not self.token:
            return {"success": False, "error": "Токен не установлен"}
        
        # Если owner_id не указан, используем текущего пользователя
        if owner_id is None:
            owner_id = self.user_id
        
        url = "https://api.vk.com/method/audio.get"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "count": 100,
            "owner_id": owner_id
        }
        
        # Пробуем два разных подхода для получения треков из плейлиста
        
        try:
            # ПОДХОД 1: Используем альбом ID (работает для некоторых аккаунтов)
            params_with_album = params.copy()
            params_with_album["album_id"] = playlist_id
            
            response1 = requests.get(url, params=params_with_album, headers=self.headers)
            data1 = response1.json()
            
            if "response" in data1 and data1["response"]["items"]:
                return {"success": True, "audio_list": data1["response"]["items"]}
            
            # ПОДХОД 2: Используем access_key если есть
            if access_key:
                params_with_access = params.copy()
                params_with_access["album_id"] = playlist_id
                params_with_access["access_key"] = access_key
                
                response2 = requests.get(url, params=params_with_access, headers=self.headers)
                data2 = response2.json()
                
                if "response" in data2 and data2["response"]["items"]:
                    return {"success": True, "audio_list": data2["response"]["items"]}
            
            # ПОДХОД 3: Пробуем получить все треки и фильтровать (запасной вариант)
            self.ui.print_warning("Прямой доступ к плейлисту недоступен. Использую обходной путь...")
            
            # Получаем все треки пользователя
            all_tracks_response = requests.get(url, params=params, headers=self.headers)
            all_tracks_data = all_tracks_response.json()
            
            if "response" in all_tracks_data:
                all_tracks = all_tracks_data["response"]["items"]
                
                # Фильтруем треки, которые относятся к нужному плейлисту
                # В VK API треки могут иметь поле album_id
                playlist_tracks = []
                for track in all_tracks:
                    if str(track.get('album_id', '')) == str(playlist_id):
                        playlist_tracks.append(track)
                
                if playlist_tracks:
                    return {"success": True, "audio_list": playlist_tracks}
            
            # Если ничего не помогло, возвращаем пустой список
            self.ui.print_info("Плейлист пуст или доступ ограничен")
            return {"success": True, "audio_list": []}
            
        except Exception as e:
            self.ui.print_error(f"Ошибка при получении треков из плейлиста: {e}")
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_recommendations(self):
        """Получить рекомендации через метод audio.getRecommendations"""
        if not self.token:
            return {"success": False, "error": "Токен не установлен"}
        
        url = "https://api.vk.com/method/audio.getRecommendations"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "count": 50,
            "shuffle": 1
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "audio_list": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                self.ui.print_warning(f"Метод getRecommendations не доступен: {error_msg}")
                return self.get_popular_music()
                
        except Exception as e:
            self.ui.print_warning(f"Ошибка в getRecommendations: {e}")
            return self.get_popular_music()

    def get_popular_music(self):
        """Получить популярную музыку через поиск"""
        import random
        query = random.choice(POPULAR_QUERIES)
        
        url = "https://api.vk.com/method/audio.search"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "q": query,
            "count": 50,
            "auto_complete": 1,
            "sort": 2
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "audio_list": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def search_audio(self, query):
        """Поиск музыки"""
        if not self.token:
            return {"success": False, "error": "Токен не установлен"}
        
        url = "https://api.vk.com/method/audio.search"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "q": query,
            "count": 50,
            "auto_complete": 1
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {
                    "success": True, 
                    "results": data["response"]["items"],
                    "total_count": data["response"]["count"]
                }
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def download_audio(self, audio_url, filename):
        """Скачать аудиозапись в указанный файл"""
        try:
            # Создаем директорию, если её нет
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            headers = self.headers.copy()
            headers.update({
                'Referer': 'https://vk.com/',
                'Origin': 'https://vk.com'
            })
            
            response = requests.get(audio_url, stream=True, headers=headers)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size:
                                self.ui.print_progress_bar(
                                    downloaded, 
                                    total_size, 
                                    prefix='Загрузка:', 
                                    suffix=f'{downloaded/1024/1024:.1f}MB/{total_size/1024/1024:.1f}MB'
                                )
                
                return True
            else:
                self.ui.print_error(f"Ошибка HTTP: {response.status_code}")
                return False
        except Exception as e:
            self.ui.print_error(f"Ошибка при скачивании: {e}")
            return False

    def get_playlists_with_access(self):
        """Получить плейлисты с дополнительной информацией"""
        if not self.token or not self.user_id:
            return {"success": False, "error": "Токен не установлен или user_id не определен"}
        
        url = "https://api.vk.com/method/audio.getPlaylists"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "owner_id": self.user_id,
            "count": 100,
            "extended": 1
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                playlists = data["response"]["items"]
                
                # Создаем кэш для быстрого поиска
                playlist_info = []
                for playlist in playlists:
                    info = {
                        'id': playlist.get('id'),
                        'owner_id': playlist.get('owner_id'),
                        'title': playlist.get('title', f'Плейлист #{playlist.get("id")}'),
                        'description': playlist.get('description', ''),
                        'count': playlist.get('count', 0),
                        'followers': playlist.get('followers', 0),
                        'access_key': playlist.get('access_key', ''),
                        'url': f"https://vk.com/music/playlist/{playlist.get('owner_id')}_{playlist.get('id')}"
                    }
                    playlist_info.append(info)
                
                return {"success": True, "playlists": playlist_info, "raw_data": playlists}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def download_track_with_name(self, track, download_dir="downloads"):
        """Скачать трек с правильным именем файла"""
        if not track:
            self.ui.print_error("Нет информации о треке")
            return False
        
        try:
            # Получаем информацию о треке
            artist = track.get('artist', 'Unknown Artist')
            title = track.get('title', 'Unknown Title')
            track_url = track.get('url')
            
            if not track_url:
                self.ui.print_error("У трека нет ссылки для скачивания")
                return False
            
            # Очищаем имя файла от недопустимых символов
            def clean_filename(filename):
                # Заменяем недопустимые символы
                invalid_chars = '<>:"/\\|?*'
                for char in invalid_chars:
                    filename = filename.replace(char, '_')
                # Убираем лишние пробелы
                filename = ' '.join(filename.split())
                # Ограничиваем длину
                if len(filename) > 200:
                    filename = filename[:200]
                return filename
            
            # Создаем имя файла в формате "Исполнитель - Название.mp3"
            filename = f"{artist} - {title}"
            filename = clean_filename(filename)
            filepath = os.path.join(download_dir, f"{filename}.mp3")
            
            # Создаем директорию, если её нет
            os.makedirs(download_dir, exist_ok=True)
            
            # Проверяем, не скачан ли уже файл
            if os.path.exists(filepath):
                self.ui.print_warning(f"Файл уже существует: {filepath}")
                overwrite = self.ui.get_input("Перезаписать? (y/n): ").strip().lower()
                if overwrite != 'y':
                    # Генерируем уникальное имя
                    counter = 1
                    name, ext = os.path.splitext(filepath)
                    while os.path.exists(filepath):
                        filepath = f"{name}_{counter}{ext}"
                        counter += 1
            
            headers = self.headers.copy()
            headers.update({
                'Referer': 'https://vk.com/',
                'Origin': 'https://vk.com'
            })
            
            self.ui.print_downloading(f"Скачивание: {artist} - {title}")
            
            response = requests.get(track_url, stream=True, headers=headers)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size:
                                self.ui.print_progress_bar(
                                    downloaded, 
                                    total_size, 
                                    prefix='Загрузка:', 
                                    suffix=f'{downloaded/1024/1024:.1f}MB/{total_size/1024/1024:.1f}MB'
                                )
                
                self.ui.print_success(f"Аудио успешно скачано: {os.path.basename(filepath)}")
                self.ui.print_info(f"Путь: {filepath}")
                
                # Добавляем метаданные ID3 теги если возможно
                try:
                    self.add_id3_tags(filepath, track)
                except:
                    pass  # Пропускаем если не удалось добавить теги
                
                return True
            else:
                self.ui.print_error(f"Ошибка HTTP: {response.status_code}")
                return False
                
        except Exception as e:
            self.ui.print_error(f"Ошибка при скачивании: {e}")
            return False

    def add_id3_tags(self, filepath, track_info):
        """Добавить ID3 теги к аудиофайлу"""
        try:
            # Пробуем импортировать mutagen
            import mutagen
            from mutagen.easyid3 import EasyID3
            
            # Пробуем добавить теги через mutagen
            try:
                audio = EasyID3(filepath)
            except mutagen.id3.ID3NoHeaderError:
                # Если файл не имеет ID3 тегов, создаем новые
                audio = EasyID3()
            
            # Устанавливаем теги
            artist = track_info.get('artist', '')
            title = track_info.get('title', '')
            album = track_info.get('album', '')
            
            if artist:
                audio['artist'] = artist
            if title:
                audio['title'] = title
            if album:
                audio['album'] = album
            
            # Добавляем дополнительные теги если есть
            if 'genre' in track_info:
                audio['genre'] = track_info['genre']
            if 'year' in track_info:
                audio['date'] = str(track_info['year'])
            
            # Сохраняем теги
            audio.save(filepath)
            self.ui.print_info("✅ ID3 теги добавлены")
            
        except ImportError:
            # mutagen не установлен
            self.ui.print_info("⚠️  Для добавления ID3 тегов установите библиотеку mutagen")
            self.ui.print_info("   pip install mutagen")
        except Exception as e:
            # Любая другая ошибка
            self.ui.print_info(f"⚠️  Не удалось добавить ID3 теги: {e}")

    def download_multiple_tracks(self, tracks, download_dir="downloads"):
        """Скачать несколько треков"""
        if not tracks:
            self.ui.print_error("Нет треков для скачивания")
            return {"success": False, "downloaded": 0, "failed": 0}
        
        total = len(tracks)
        downloaded = 0
        failed = 0
        
        self.ui.print_info(f"Начинаю скачивание {total} треков...")
        
        for i, track in enumerate(tracks, 1):
            artist = track.get('artist', 'Unknown Artist')
            title = track.get('title', 'Unknown Title')
            
            self.ui.print_info(f"[{i}/{total}] Скачиваю: {artist} - {title}")
            
            if self.download_track_with_name(track, download_dir):
                downloaded += 1
            else:
                failed += 1
        
        return {
            "success": True,
            "downloaded": downloaded,
            "failed": failed,
            "total": total
        }

    def get_formatted_track_info(self, track):
        """Получить отформатированную информацию о треке"""
        artist = track.get('artist', 'Unknown Artist')
        title = track.get('title', 'Unknown Title')
        
        # Очистка от лишних символов
        artist = artist.strip()
        title = title.strip()
        
        # Удаляем повторяющиеся пробелы
        artist = ' '.join(artist.split())
        title = ' '.join(title.split())
        
        return {
            'artist': artist,
            'title': title,
            'full_name': f"{artist} - {title}",
            'url': track.get('url'),
            'duration': track.get('duration', 0),
            'album': track.get('album', ''),
            'genre': track.get('genre', ''),
            'year': track.get('year', ''),
            'original_track': track
        }

    def get_track_download_path(self, track, download_dir="downloads"):
        """Получить путь для скачивания трека с правильным именем"""
        track_info = self.get_formatted_track_info(track)
        filename = f"{track_info['artist']} - {track_info['title']}.mp3"
        
        # Очистка имени файла
        def clean_filename(name):
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                name = name.replace(char, '_')
            name = ' '.join(name.split())
            if len(name) > 200:
                name = name[:200]
            return name
        
        filename = clean_filename(filename)
        filepath = os.path.join(download_dir, filename)
        
        # Проверяем уникальность имени
        counter = 1
        original_filepath = filepath
        while os.path.exists(filepath):
            name, ext = os.path.splitext(original_filepath)
            filepath = f"{name}_{counter}{ext}"
            counter += 1
        
        return filepath

    def test_playlist_access(self):
        """Тестирование доступа к плейлистам"""
        if not self.token:
            return {"success": False, "error": "Токен не установлен"}
        
        test_results = []
        
        # Тест 1: Проверка базового доступа
        validity = self.check_token_validity()
        if validity["valid"]:
            test_results.append({"test": "Токен", "success": True})
        else:
            test_results.append({"test": "Токен", "success": False, "error": validity.get('error_msg')})
        
        # Тест 2: Проверка метода getPlaylists
        url = "https://api.vk.com/method/audio.getPlaylists"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "owner_id": self.user_id,
            "count": 1
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                count = data["response"]["count"]
                test_results.append({"test": "audio.getPlaylists", "success": True, "count": count})
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                error_code = data.get("error", {}).get("error_code", 0)
                test_results.append({"test": "audio.getPlaylists", "success": False, "error": error_msg, "code": error_code})
        except Exception as e:
            test_results.append({"test": "audio.getPlaylists", "success": False, "error": str(e)})
        
        # Тест 3: Проверка метода audio.get
        url2 = "https://api.vk.com/method/audio.get"
        params2 = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "owner_id": self.user_id,
            "count": 1
        }
        
        try:
            response2 = requests.get(url2, params=params2, headers=self.headers)
            data2 = response2.json()
            
            if "response" in data2:
                count2 = data2["response"]["count"]
                test_results.append({"test": "audio.get", "success": True, "count": count2})
            else:
                error_msg2 = data2.get("error", {}).get("error_msg", "Неизвестная ошибка")
                error_code2 = data2.get("error", {}).get("error_code", 0)
                test_results.append({"test": "audio.get", "success": False, "error": error_msg2, "code": error_code2})
        except Exception as e:
            test_results.append({"test": "audio.get", "success": False, "error": str(e)})
        
        return {"success": True, "tests": test_results}
