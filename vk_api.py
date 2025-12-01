import requests
import logging
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

    def load_token_from_file(self, filename=TOKEN_FILE):
        """Загрузить токен из файла"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    token = f.read().strip()
                    if token:
                        self.set_token(token)
                        self.ui.print_success(f"Токен загружен из файла {filename}")
                        return True
            self.ui.print_error(f"Файл {filename} не найден или пуст")
            return False
        except Exception as e:
            self.ui.print_error(f"Ошибка при чтении файла: {e}")
            return False

    def save_token_to_file(self, filename=TOKEN_FILE):
        """Сохранить токен в файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.token)
            self.ui.print_success(f"Токен сохранен в файл {filename}")
            return True
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
        self.set_token(token)
        
        validity = self.check_token_validity()
        if not validity["valid"]:
            self.ui.print_error(f"Токен невалиден: {validity.get('error_msg')}")
            self.token = old_token  # Восстанавливаем старый токен
            return False
        
        self.ui.print_success("Токен валиден!")
        
        # Предлагаем сохранить токен
        save = self.ui.get_input("Сохранить токен в файл? (y/n): ").strip().lower()
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
                return {"valid": False, "error_msg": error_msg}
                
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
            "count": 50
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if "response" in data:
                return {"success": True, "playlists": data["response"]["items"]}
            else:
                error_msg = data.get("error", {}).get("error_msg", "Неизвестная ошибка")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            return {"success": False, "error": f"Ошибка запроса: {e}"}

    def get_playlist_tracks(self, playlist_id):
        """Получить треки из плейлиста"""
        if not self.token or not self.user_id:
            return {"success": False, "error": "Токен не установлен или user_id не определен"}
        
        url = "https://api.vk.com/method/audio.get"
        params = {
            "access_token": self.token,
            "v": VK_API_VERSION,
            "count": 100,
            "album_id": playlist_id,
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
        """Скачать аудиозапись"""
        try:
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
            return False
        except Exception as e:
            self.ui.print_error(f"Ошибка при скачивании: {e}")
            return False