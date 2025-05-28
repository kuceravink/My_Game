import pygame
import sys
import importlib
import main

# Инициализация Pygame
pygame.init()

# Настройки экрана
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cosmopoliten - Меню")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (70, 130, 255)

# Шрифты
font_large = pygame.font.SysFont("Arial", 50, bold=True)
font_small = pygame.font.SysFont("Arial", 30)

def show_menu():
    """Функция отображения меню."""
    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    mouse_clicked = True

        # Отрисовка меню
        screen.fill(BLACK)

        # Название игры
        title = font_large.render("Cosmopoliten", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        # Кнопка "Старт"
        start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 300, 200, 50)
        pygame.draw.rect(screen, BLUE, start_button, border_radius=10)
        start_text = font_small.render("Старт", True, WHITE)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 310))

        # Проверка нажатия на кнопку
        if start_button.collidepoint(mouse_pos) and mouse_clicked:
            return  # Выходим из меню и запускаем игру

        pygame.display.flip()

def run_game():
    """Запускает game.py как отдельный скрипт"""
    with open("game.py", "r", encoding="utf-8") as f:
        game_code = f.read()
    # Создаем свой словарь для глобальных переменных игры
    game_globals = {"__name__": "__main__"}
    exec(game_code, game_globals)


# Главный цикл
if __name__ == "__main__":
    
    show_menu()  # Показываем меню
 # Запускаем игру

    # После завершения игры (если вернулись в меню)
    pygame.quit()
    sys.exit()