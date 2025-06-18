import pygame
from settings import *
from game import Game

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('COSMOPOLITEN')
    clock = pygame.time.Clock()
    
    game = Game(screen, clock)
    game.run()

if __name__ == "__main__":
    main()