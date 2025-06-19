import pygame
from settings import *
from game import Game

def main():
    """Основная точка входа в приложение. Инициализирует и запускает игру.
    """
    pygame.init()  # Инициализация всех модулей pygame
    pygame.mixer.init()  # Инициализация звуковой системы
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Создание игрового окна
    pygame.display.set_caption('COSMOPOLITEN')  # Установка заголовка окна
    clock = pygame.time.Clock()  # Создание объекта времени для контроля FPS
    
    game = Game(screen, clock)  # Создание экземпляра игры

    try:
        game.run()
    finally:
        # Сохраняем рекорд при закрытии игры
        if hasattr(game, 'record'):
            save_record(game.record)
        pygame.quit()

if __name__ == "__main__":
    main()