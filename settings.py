import pygame
import os
from os import path

# Screen dimensions
WIDTH = 480
HEIGHT = 600
FPS = 144

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)

# Game states
MENU = 0
GAME = 1
GAME_OVER = 2

# Paths
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'music')

# Font
font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)