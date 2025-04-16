import pygame
import random
import os 
from PIL import Image, ImageSequence


WIDTH = 480
HEIGHT = 600
FPS = 144

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

pygame.init()
pygame.mixer.init() 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('My_first_Gaame')
clock = pygame.time.Clock()


def load_gif(path):
    gif = Image.open(path)  # Открываем GIF с помощью Pillow
    frames = []  # Сюда будем складывать кадры в формате Pygame

    for frame in ImageSequence.Iterator(gif):  # Перебираем все кадры GIF
        frame = frame.convert("RGBA")  # Конвертируем в RGBA (чтобы был альфа-канал, если есть прозрачность)
        pygame_frame = pygame.image.fromstring(
            frame.tobytes(),  # Байтовое представление изображения
            frame.size,      # Размер кадра (ширина, высота)
            "RGBA"           # Формат цвета (Red, Green, Blue, Alpha)
        )
        frames.append(pygame_frame)  # Добавляем кадр в список

    return frames  # Возвращаем список кадров





#инициализируем класс героя, он имеет image и rect(это его вид, а другое это прямоугольник для отслеживания)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # Загружаем GIF и получаем список кадров
        self.frames = load_gif('C:\\Users\\kucer\\OneDrive\\Desktop\\My_Game\\img\\ship1a.gif')  # Используем нашу функцию из предыдущего шага
        self.current_frame = 0
        self.animation_speed = 0.1  # Скорость анимации (можно регулировать)
        self.frame_count = 0

        # Начальное изображение
        self.image = self.frames[self.current_frame]
        self.image.set_colorkey(WHITE)  # Удаляем фон если нужно
        self.size_ = (52, 52)
        self.image = pygame.transform.scale(self.image, self.size_)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

    def update(self):
        # Движение
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_LEFT]:
            self.speedx = -3
        if keystate[pygame.K_RIGHT]:
            self.speedx = 3
        self.rect.x += self.speedx
        if keystate[pygame.K_UP]:
            self.speedy = -3
        if keystate[pygame.K_DOWN]:
            self.speedy = 3
        self.rect.y += self.speedy
        # Границы экрана

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:  # Верхняя граница
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:  # Нижняя граница
            self.rect.bottom = HEIGHT

        # Анимация
        self.frame_count += 1
        if self.frame_count >= self.animation_speed * 60:  # 60 FPS
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.image.set_colorkey(WHITE)  # Обновляем colorkey для нового кадра

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)


class Mobs(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('C:\\Users\\kucer\\Downloads\\Layered Rock.png')
        self.size_ = (38, 38)
        self.image = pygame.transform.scale(self.image, self.size_ )
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(2, 5)
        self.speedx = random.randrange(-2, 2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 5)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('C:\\Users\\kucer\\Downloads\\bullet.png')
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
player = Player()
bullets = pygame.sprite.Group()
all_sprites.add(player)
for i in range(5):
    m = Mobs()
    all_sprites.add(m)
    mobs.add(m)


running = True
while running:
    #контролируем уровень кадров в секунду
    clock.tick(FPS)

    for event in pygame.event.get():
        # делаем возможноть закрыть окно крестиком
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    #обновление
    all_sprites.update()
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        m = Mobs()
        all_sprites.add(m)
        mobs.add(m)


    #проверка не ударил ли моб игрока
    hits = pygame.sprite.spritecollide(player, mobs, False)
    if hits:
        running = False

    # Рендеринг
    screen.fill(BLACK)
    #отрисовываем все спрайты
    all_sprites.draw(screen)
    # поворачиваем экран к пользователю(мы отрисовали только заднюю сторону)
    pygame.display.flip()

pygame.quit()

