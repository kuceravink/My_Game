import pygame
from os import path

"""Модуль настроек игры, содержащий константы и вспомогательные функции.
"""

# размеры экрана и частота кадров
WIDTH = 480 
HEIGHT = 600  
FPS = 144  

# цвета
WHITE = (255, 255, 255)  
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)  
LIGHT_BLUE = (173, 216, 230)  
BOSS_COLOR = (255, 50, 50)  
BOSS_TEXT_COLOR = (255, 255, 0)

# магические числа
BONUS_CHANCE = 0.9 # 10%
BOSS_HIT = 100



# состояния игры
MENU = 0  
GAME = 1 
GAME_OVER = 2 
PAUSE = 3

# пути
img_dir = path.join(path.dirname(__file__), 'img')  
snd_dir = path.join(path.dirname(__file__), 'music') 
RECORD_FILE = path.join(path.dirname(__file__), 'record.dat')

def load_record():
    """Загружает рекорд из файла."""
    try:
        with open(RECORD_FILE, 'rb') as f:
            return int(f.read())
    except:
        return 0

def save_record(score):
    """Сохраняет новый рекорд."""
    with open(RECORD_FILE, 'wb') as f:
        f.write(str(score).encode())

# шрифт
font_name = pygame.font.match_font('impact') 

def draw_text(surf, text, size, x, y):
    """Отрисовывает текст на указанной поверхности.
    
    Args:
        surf (pygame.Surface): Поверхность для отрисовки текста
        text (str): Текст для отображения
        size (int): Размер шрифта
        x (int): X-координата позиции текста (центрируется)
        y (int): Y-координата верхнего края текста
    """
    font = pygame.font.Font(font_name, size)       # Создание объекта шрифта
    text_surface = font.render(text, True, WHITE)  # Генерация поверхности с текстом
    text_rect = text_surface.get_rect()            # Получение прямоугольника текста
    text_rect.midtop = (x, y)                      # Установка позиции текста
    surf.blit(text_surface, text_rect)             # Отрисовка текста на поверхности