import pygame
import random
from os import path
from PIL import Image, ImageSequence
import sys

#480
#600
WIDTH = 480
HEIGHT = 600
FPS = 144

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)

MENU = 0
GAME = 1
GAME_OVER = 2
game_state = MENU

pygame.init()
pygame.mixer.init() 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('COSMOPOLITEN')
clock = pygame.time.Clock()


title_font = pygame.font.SysFont('Arial', 48, bold=True)
button_font = pygame.font.SysFont('Arial', 32)

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'music')
bust_img = {}
bust_img['shield'] = pygame.image.load(path.join(img_dir, 'shield.png')).convert()
bust_img['heart'] = pygame.image.load(path.join(img_dir, 'heart.png')).convert()
shoot_m = pygame.mixer.Sound(path.join(snd_dir, 'Laser.wav'))
expl = pygame.mixer.Sound(path.join(snd_dir, 'explosion01.wav'))
expl.set_volume(0.09)
pygame.mixer.music.load(path.join(snd_dir, 'hull_et_belle.ogg'))
pygame.mixer.music.set_volume(0.4)
heart = pygame.image.load(path.join(img_dir, 'heart pixel art 32x32.png')).convert()
heart.set_colorkey(BLACK)
background = pygame.image.load('C:\\Users\\kucer\\OneDrive\\Desktop\\My_Game\\bg_space_seamless.png').convert()
background = pygame.transform.scale(background, (480, 600))
background_rect = background.get_rect()

blast = {}
blast['bg'] = []
blast['sm'] = []
blast['player'] = []
for i in range(9):
    name_img = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, name_img)).convert()
    img.set_colorkey(BLACK)
    img_bg = pygame.transform.scale(img, (75, 75))
    blast['bg'].append(img_bg)
    img_sm = pygame.transform.scale(img, (32, 32))
    blast['sm'].append(img_sm)
    name_img = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, name_img)).convert()
    img.set_colorkey(BLACK)
    blast['player'].append(img)

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

font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    _LENGTH = 100
    _HEIGHT = 10
    fill = (pct / 100) * _LENGTH
    outline_rect = pygame.Rect(x, y, _LENGTH, _HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, _HEIGHT)
    pygame.draw.rect(surf, WHITE, fill_rect)
    pygame.draw.rect(surf, BLUE, outline_rect, 2)

def draw_hearts(surf, x, y, heart, img):
    for i in range(heart):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

# Функции для работы с меню
def draw_menu():
    screen.blit(background, background_rect)
    
    # Название игры
    title = title_font.render("COSMOPOLITEN", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
    
    # Кнопка "Старт"
    start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, LIGHT_BLUE, start_button, border_radius=10)
    start_text = button_font.render("СТАРТ", True, BLACK)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 10))
    
    return start_button

def draw_game_over(score):
    screen.blit(background, background_rect)
    
    # Текст "Игра окончена"
    game_over_text = title_font.render("ИГРА ОКОНЧЕНА", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))
    
    # Счет
    score_text = button_font.render(f"Счет: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 3))
    
    # Кнопка "Рестарт"
    restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, LIGHT_BLUE, restart_button, border_radius=10)
    restart_text = button_font.render("ЗАНОВО", True, BLACK)
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))
    
    return restart_button

def reset_game():
    global all_sprites, mobs, bullets, bust, player, score
    
    # Очищаем все группы спрайтов
    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    bust = pygame.sprite.Group()
    
    # Создаем нового игрока
    player = Player()
    all_sprites.add(player)
    
    # Создаем мобов
    for i in range(5):
        mobspawn()
    
    # Сбрасываем счет
    score = 0
    
    # Запускаем музыку
    pygame.mixer.music.play(loops=-1)

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
        self.image.set_colorkey(WHITE)
        self.size_ = (52, 52)
        self.image = pygame.transform.scale(self.image, self.size_)
        self.rect = self.image.get_rect()
        self.radius = 25
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.health = 100
        self.shoot_pause = 250
        self.last_shot = pygame.time.get_ticks() 
        self.hearts = 3
        self.hides = False
        self.hide_time = pygame.time.get_ticks()



    def update(self):
        if self.hides and pygame.time.get_ticks() - self.hide_time > 100:
            self.hides = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10


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
        if keystate[pygame.K_SPACE]:
            self.shoot()
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
        if self.frame_count >= self.animation_speed * 144:  # 144 FPS
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.image.set_colorkey(WHITE)  # Обновляем colorkey для нового кадра

        

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_pause:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_m.play()

    def hide(self):
    # временно скрыть игрока
        self.hides = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Mobs(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Загружаем изображение
        self.image_orig = pygame.image.load('C:\\Users\\kucer\\Downloads\\Layered Rock.png')
        
        # Генерируем случайный размер в пределах заданного диапазона
        min_size = 25  # минимальный размер
        max_size = 55  # максимальный размер
        size = random.randrange(min_size, max_size)
        self.size_ = (size, size)
        
        # Масштабируем изображение
        self.image_orig = pygame.transform.scale(self.image_orig, self.size_)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        
        # Радиус для коллизий (можно оставить пропорциональным или тоже сделать случайным)
        self.radius = int(self.rect.width * .85 / 2)
        
        # Начальная позиция
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        
        # Скорости (можно сделать зависимыми от размера - маленькие быстрее)
        self.speedy = random.randrange(2, 5)
        self.speedx = random.randrange(-2, 2)
        
        # Вращение
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
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
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            # При респавне тоже генерируем новый случайный размер
            size = random.randrange(25, 55)
            self.size_ = (size, size)
            self.image_orig = pygame.transform.scale(pygame.image.load('C:\\Users\\kucer\\Downloads\\Layered Rock.png'), self.size_)
            self.image = self.image_orig.copy()
            self.rect = self.image.get_rect()
            self.radius = int(self.rect.width * .85 / 2)
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 5)
            self.speedx = random.randrange(-2, 2)

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

class Blast(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = blast[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_upd = 50
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_upd:
            self.last_update = now
            self.frame += 1
            if self.frame == len(blast[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = blast[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Bust(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = 'heart' #заглушка!!!!!!
        self.image = bust_img[self.type]
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
player = Player()
bullets = pygame.sprite.Group()
bust = pygame.sprite.Group()
all_sprites.add(player)

def mobspawn():
    m = Mobs()
    all_sprites.add(m)
    mobs.add(m)

for i in range(5):
    mobspawn()

score = 0
pygame.mixer.music.play(loops=-1)
running = True 


while running:
    #контролируем уровень кадров в секунду
    clock.tick(FPS)

    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    for event in pygame.event.get():
        # делаем возможноть закрыть окно крестиком
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                mouse_clicked = True
    if game_state == MENU:
        start_button = draw_menu()
        if mouse_clicked and start_button.collidepoint(mouse_pos):
            reset_game()
            game_state = GAME

    elif game_state == GAME:
        #обновление
        all_sprites.update()

        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            m = Mobs()
            expl.play()
            score += 50 - hit.radius
            all_sprites.add(m)
            mobs.add(m) 
            blst = Blast(hit.rect.center, 'bg')
            all_sprites.add(blst)
            mx_score = 0
            next_threshold = mx_score + 500
            if score >= next_threshold:
                mobspawn()  
                mx_score = next_threshold
            if random.random() > 0.9:
                blst = Bust(hit.rect.center)
                all_sprites.add(blst)
                bust.add(blst)

        
            

        #проверка не ударил ли моб игрока
        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            player.health -= hit.radius * 2
            blst = Blast(hit.rect.center, 'sm')
            all_sprites.add(blst)
            mobspawn()
            if player.health < 0:
                all_sprites.add(Blast(player.rect.center, 'player'))
                player.hide()
                player.hearts -= 1
                player.health = 100




        if not player.alive() and not Blast(player.rect.center, 'player').alive():
            running = False

        if player.hearts == 0:
            game_state = GAME_OVER

        hits = pygame.sprite.spritecollide(player, bust, True)
        for hit in hits:
            if hit.type == 'heart':
                player.health += random.randrange(10, 30)
            if player.health >= 100:
                player.health = 100
            if hit.type == 'shield':
                pass


        # Рендеринг
        screen.fill(BLACK)
        screen.blit(background, background_rect)
        #отрисовываем все спрайты
        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)
        draw_health(screen, 5, 5, player.health)
        draw_hearts(screen, WIDTH - 100, 5, player.hearts, heart)
    elif game_state == GAME_OVER:
        restart_button = draw_game_over(score)
        if mouse_clicked and restart_button.collidepoint(mouse_pos):
            reset_game()
            game_state = GAME
    # поворачиваем экран к пользователю(мы отрисовали только заднюю сторону)
    pygame.display.flip()



pygame.quit()

