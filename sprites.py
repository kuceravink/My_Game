import pygame
import random
from settings import *
from os import path
from PIL import Image, ImageSequence

class Boss(pygame.sprite.Sprite):
    """Класс босса - особо крупного и прочного метеорита.
    """
    
    def __init__(self, game):
        """Инициализация обьекта босс.
        
        Args:
            game (Game): Ссылка на основной объект игры
        """
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.health = 3  # Босс требует 3 попадания
        
        # Загрузка особого изображения для босса
        self.image_orig = pygame.image.load(path.join(img_dir, 'Layered Rock.png')).convert_alpha()
        self.image_orig = pygame.transform.scale(self.image_orig, (120, 120))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = 35  # Больший радиус коллизий
        
        # Появление в случайной позиции сверху
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        
        # Скорость немного ниже обычных метеоритов
        self.speedy = random.randrange(1, 3)
        self.speedx = random.randrange(-1, 1)
        
        # Эффект "дрожания" для выделения босса
        self.shake_timer = pygame.time.get_ticks()
        self.shake_offset = 0

    def update(self):
        """Обновление позиции босса с эффектом дрожания."""
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # Эффект дрожания (каждые 100ms)
        now = pygame.time.get_ticks()
        if now - self.shake_timer > 100:
            self.shake_timer = now
            self.shake_offset = random.randrange(-3, 3)
            self.rect.x += self.shake_offset
        
        # Респавн при выходе за границы
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -100)
            self.speedy = random.randrange(1, 3)


class Explosion(pygame.sprite.Sprite):
    """Класс анимации взрыва.
    """
    
    def __init__(self, game, center, size):
        """Инициализация взрыва.
        
        Args:
            game (Game): Ссылка на основной объект игры
            center (tuple): Координаты центра взрыва (x, y)
            size (str): Тип размера ('bg', 'sm' или 'player')
        """
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.size = size
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        
        self.images = []
        for i in range(9):
            if size == 'player':
                filename = f'sonicExplosion0{i}.png'
            else:
                filename = f'regularExplosion0{i}.png'
            
            img = pygame.image.load(path.join(img_dir, filename)).convert_alpha()
            if size == 'bg':
                img = pygame.transform.scale(img, (75, 75))
            elif size == 'sm':
                img = pygame.transform.scale(img, (32, 32))
            self.images.append(img)
        
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        """Обновление анимации взрыва.
        Переключает кадры анимации с заданной частотой и удаляет спрайт
        по завершении анимации.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.images):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.images[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Player(pygame.sprite.Sprite):
    """Класс игрока, управляемого пользователем.
    """
    
    def __init__(self, game):
        """Инициализация игрока.
        
        Args:
            game (Game): Ссылка на основной объект игры
        """
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.load_gif()
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        self.health = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.hearts = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.invincible = False
        self.invincible_timer = pygame.time.get_ticks()

    def load_gif(self):
        """Загрузка GIF-анимации корабля с обработкой прозрачности."""
        gif_path = path.join(img_dir, 'ship1a.gif')
        gif = Image.open(gif_path)
        self.frames = []
        
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert('RGBA')
            data = frame.tobytes()
            temp_surface = pygame.image.fromstring(data, frame.size, 'RGBA')
            
            # Удаление белого фона
            pixels = pygame.PixelArray(temp_surface)
            white = temp_surface.map_rgb((255, 255, 255, 255))
            pixels.replace(white, (0, 0, 0, 0))
            del pixels
            
            temp_surface = pygame.transform.scale(temp_surface, (52, 52))
            temp_surface = temp_surface.convert_alpha()
            self.frames.append(temp_surface)

    def update(self):
        """Обновление состояния игрока.
        
        Обрабатывает:
        1 Анимацию корабля
        2 Состояние неуязвимости
        3 Управление с клавиатуры
        4 Границы экрана
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
        
        # Логика респавна после смерти
        if self.hidden and now - self.hide_timer > 100:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
            self.invincible = True
            self.invincible_timer = now
        
        # Логика неуязвимости
        if self.invincible and now - self.invincible_timer > 3000:
            self.invincible = False
        
        # Эффект мигания при неуязвимости
        if self.invincible:
            if now % 200 < 100:
                self.image.set_alpha(150)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
        
        # Обработка управления
        keystate = pygame.key.get_pressed()
        self.speedx = 0
        self.speedy = 0
        
        if keystate[pygame.K_LEFT]:
            self.speedx = -3
        if keystate[pygame.K_RIGHT]:
            self.speedx = 3
        if keystate[pygame.K_UP]:
            self.speedy = -3
        if keystate[pygame.K_DOWN]:
            self.speedy = 3
        if keystate[pygame.K_SPACE]:
            self.shoot()
        
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        # Ограничение движения в пределах экрана
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def shoot(self):
        """Создание новой пули при выстреле."""
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.game, self.rect.centerx, self.rect.top)
            self.game.all_sprites.add(bullet)
            self.game.bullets.add(bullet)
            self.game.shoot_sound.play()

    def hide(self):
        """Скрытие игрока (используется при смерти)."""
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

class Mob(pygame.sprite.Sprite):
    """Класс вражеского объекта (метеорита).
    """
    
    def __init__(self, game):
        """Инициализация метеорита.
        
        Args:
            game (Game): Ссылка на основной объект игры
        """
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image_orig = pygame.image.load(path.join(img_dir, 'Layered Rock.png')).convert_alpha()
        size = random.randrange(25, 55)
        self.image_orig = pygame.transform.scale(self.image_orig, (size, size))
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(size * 0.85 / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.randrange(-2, 2)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        """Обновление вращения метеорита."""
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        """Обновление положения метеорита.
        """
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 4)

class Bullet(pygame.sprite.Sprite):
    """Класс пули, выпущенной игроком.
    """
    
    def __init__(self, game, x, y):
        """Инициализация пули.
        
        Args:
            game (Game): Ссылка на основной объект игры
            x (int): Горизонтальная позиция создания
            y (int): Вертикальная позиция создания
        """
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.image.load(path.join(img_dir, 'bullet.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """Обновление положения пули.
        
        Удаляет пулю при выходе за верхнюю границу экрана.
        """
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Bust(pygame.sprite.Sprite):
    """Класс объекта улучшения.
    """
    
    def __init__(self, game, center):
        """Инициализация улучшения.
        
        Args:
            game (Game): Ссылка на основной объект игры
            center (tuple): Координаты центра (x, y)
        """
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.type = random.choice(['heart', 'shield'])
        # Временная заглушка - всегда сердце
        self.image = pygame.image.load(path.join(img_dir, 'heart.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        """Обновление положения улучшения.
        
        Удаляет улучшение при выходе за нижнюю границу экрана.
        """
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()