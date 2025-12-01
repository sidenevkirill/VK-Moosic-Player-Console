import os
from config import Colors

class ConsoleUI:
    """Класс для красивого консольного интерфейса"""
    
    @staticmethod
    def clear_screen():
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header(title):
        """Печать заголовка"""
        width = 60
        print("\n" + "═" * width)
        print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{title.center(width)}{Colors.RESET}")
        print("═" * width)
    
    @staticmethod
    def print_menu_item(number, text, color=Colors.BRIGHT_WHITE):
        """Печать пункта меню"""
        print(f"{Colors.BRIGHT_YELLOW}{number:>2}.{Colors.RESET} {color}{text}{Colors.RESET}")
    
    @staticmethod
    def print_success(msg):
        """Печать успешного сообщения"""
        print(f"{Colors.BRIGHT_GREEN}✓ {msg}{Colors.RESET}")
    
    @staticmethod
    def print_error(msg):
        """Печать сообщения об ошибке"""
        print(f"{Colors.BRIGHT_RED}✗ {msg}{Colors.RESET}")
    
    @staticmethod
    def print_warning(msg):
        """Печать предупреждения"""
        print(f"{Colors.BRIGHT_YELLOW}⚠ {msg}{Colors.RESET}")
    
    @staticmethod
    def print_info(msg):
        """Печать информационного сообщения"""
        print(f"{Colors.BRIGHT_CYAN}ℹ {msg}{Colors.RESET}")
    
    @staticmethod
    def print_playing(msg):
        """Печать сообщения о воспроизведении"""
        print(f"{Colors.BRIGHT_MAGENTA}▶ {msg}{Colors.RESET}")
    
    @staticmethod
    def print_downloading(msg):
        """Печать сообщения о загрузке"""
        print(f"{Colors.BRIGHT_BLUE}↓ {msg}{Colors.RESET}")
    
    @staticmethod
    def print_box(content, title=None, color=Colors.BRIGHT_CYAN):
        """Печать текста в рамке"""
        lines = content.split('\n')
        max_len = max(len(line) for line in lines) + 4
        
        print(f"{color}┌{'─' * (max_len - 2)}┐{Colors.RESET}")
        if title:
            print(f"{color}│ {Colors.BOLD}{title.center(max_len - 4)}{Colors.RESET}{color} │{Colors.RESET}")
            print(f"{color}├{'─' * (max_len - 2)}┤{Colors.RESET}")
        for line in lines:
            print(f"{color}│ {line.ljust(max_len - 4)} │{Colors.RESET}")
        print(f"{color}└{'─' * (max_len - 2)}┘{Colors.RESET}")
    
    @staticmethod
    def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
        """Печать прогресс-бара"""
        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '░' * (length - filled_length)
        print(f'\r{prefix} │{Colors.BRIGHT_GREEN}{bar}{Colors.RESET}│ {percent}% {suffix}', end='\r')
        if iteration == total:
            print()
    
    @staticmethod
    def print_centered(text, color=Colors.BRIGHT_WHITE):
        """Печать центрированного текста"""
        width = 60
        print(f"{color}{text.center(width)}{Colors.RESET}")
    
    @staticmethod
    def get_input(prompt, color=Colors.BRIGHT_YELLOW):
        """Получение ввода с цветным промптом"""
        return input(f"{color}{prompt}{Colors.RESET}")