import pygame
import random
from settings import *
from sprites import *

class Game:
    """Основной класс игры, управляющий игровым процессом, состоянием и отрисовкой.
    """
    
    def __init__(self, screen, clock):
        """Инициализация обьекта игры.
        
        
        Args:
            screen (pygame.Surface): Основная поверхность для отрисовки игры
            clock (pygame.time.Clock): Объект для контроля частоты кадров
        """
        self.screen = screen
        self.clock = clock
        self.load_data()
        self.reset()
        self.mob_spawn_score = 400 
        self.max_mobs = 12  
        self.base_mob_count = 5
        self.next_boss_score = 2000  # следующий босс появится
        self.record = load_record()

    def load_data(self):
        """Загружает некоторые необходимые ресурсы (звуки, изображения)."""
        self.shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'Laser.wav'))
        self.expl_sound = pygame.mixer.Sound(path.join(snd_dir, 'explosion01.wav'))
        self.expl_sound.set_volume(0.09)
        pygame.mixer.music.load(path.join(snd_dir, 'hull_et_belle.ogg'))
        pygame.mixer.music.set_volume(0.4)
        

        
        self.background = pygame.image.load(path.join(img_dir, 'bg_space_seamless.png')).convert()
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        self.background_rect = self.background.get_rect()
        
        self.heart_img = pygame.image.load(path.join(img_dir, 'heart pixel art 32x32.png')).convert_alpha()
        
    def reset(self):
        """Сбрасывает игровое состояние к начальным значениям."""
        self.all_sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.bust = pygame.sprite.Group()
        self.record = load_record()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        for i in range(5): # начальное кол-во мобов на карте
            self.spawn_mob()
            
        self.score = 0
        self.game_state = MENU
        self.boss_active = False
        self.next_boss_score = 2000
        pygame.mixer.music.play(loops=-1)
        
    def spawn_mob(self):
        """Создает нового моба и добавляет его в группы спрайтов."""
        m = Mob(self)
        self.all_sprites.add(m)
        self.mobs.add(m)
        
    def spawn_boss(self):
        """Создает босса и добавляет его в группы спрайтов."""
        if not self.boss_active:
            self.boss = Boss(self)
            self.all_sprites.add(self.boss)
            self.boss_active = True
            
        
    def run(self):
        """Основной игровой цикл."""
        self.running = True
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            
    def events(self):
        """Обрабатывает события игры (нажатия клавиш, закрытие окна)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                # Обработка паузы по ESC
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == GAME:
                        self.game_state = PAUSE
                        pygame.mixer.music.pause()  # Приостанавливаем музыку
                    elif self.game_state == PAUSE:
                        self.game_state = GAME
                        pygame.mixer.music.unpause()  # Возобновляем музыку
                
                # Выход по ESC из других состояний
                if event.key == pygame.K_ESCAPE and self.game_state in (MENU, GAME_OVER):
                    self.running = False
                
    def update(self):
        """Обновляет игровое состояние."""
        if self.game_state == GAME_OVER:
            if self.score > self.record:
                self.record = self.score
                save_record(self.record)
        if self.game_state == GAME:
            # Увеличение сложности
            if self.score > self.mob_spawn_score:
                self.mob_spawn_score += 400  # увеличение сложности каждые 400 очков
                if len(self.mobs) < self.max_mobs: 
                    self.spawn_mob()

            # Спавн босса
            if self.score >= self.next_boss_score and not self.boss_active:
                self.spawn_boss()
                self.next_boss_score += 2000  # Следующий босс через +2000

            self.all_sprites.update()
            
            # Обработка попаданий пуль
            hits = pygame.sprite.groupcollide(self.mobs, self.bullets, True, True)
            for hit in hits:
                self.expl_sound.play()
                self.score += 50 - hit.radius
                expl = Explosion(self, hit.rect.center, 'bg')
                self.all_sprites.add(expl)
                self.spawn_mob()
                
                if random.random() > BONUS_CHANCE:
                    b = Bust(self, hit.rect.center)
                    self.all_sprites.add(b)
                    self.bust.add(b)
            
            # Обработка столкновений с боссом
            if self.boss_active:
                boss_hits = pygame.sprite.spritecollide(self.boss, self.bullets, True)
                for bullet in boss_hits:
                    self.boss.health -= 1

                    if self.boss.health <= 0:
                        self.score += 500  # Награда за босса
                        expl = Explosion(self, self.boss.rect.center, 'bg')
                        self.all_sprites.add(expl)
                        self.boss.kill()
                        self.boss_active = False

            # Обработка столкновений игрока с боссом
            if self.boss_active:
                boom = pygame.sprite.spritecollide(self.player, pygame.sprite.Group(self.boss), True)
                for hit in boom:
                    self.player.health -= BOSS_HIT
                    expl = Explosion(self, hit.rect.center, 'sm')
                    self.all_sprites.add(expl)
                    self.boss_active = False
                    player_expl = Explosion(self, self.player.rect.center, 'player')
                    self.all_sprites.add(player_expl)
                    self.player.hide()
                    self.player.hearts -= 1
                    self.player.health = 100
                        
                    if self.player.hearts <= 0:
                        self.game_state = GAME_OVER

            # Обработка столкновений игрока
            if not self.player.hidden and not self.player.invincible:
                hits = pygame.sprite.spritecollide(self.player, self.mobs, True, pygame.sprite.collide_circle)
                for hit in hits:
                    self.player.health -= hit.radius * 2
                    expl = Explosion(self, hit.rect.center, 'sm')
                    self.all_sprites.add(expl)
                    self.spawn_mob()
                    
                    if self.player.health <= 0:
                        player_expl = Explosion(self, self.player.rect.center, 'player')
                        self.all_sprites.add(player_expl)
                        self.player.hide()
                        self.player.hearts -= 1
                        self.player.health = 100
                        
                        if self.player.hearts <= 0:
                            self.game_state = GAME_OVER
            
            # Обработка бонусов
            hits = pygame.sprite.spritecollide(self.player, self.bust, True)
            for hit in hits:
                if hit.type == 'heart':
                    self.player.health = min(100, self.player.health + random.randrange(10, 30))
    
    def draw(self):
        """Отрисовывает все игровые объекты."""
        self.screen.blit(self.background, self.background_rect)
        
        if self.game_state == MENU:
            self.draw_menu()
        elif self.game_state == PAUSE:
            self.all_sprites.draw(self.screen)
            self.draw_pause_screen()
        elif self.game_state == GAME:
            self.all_sprites.draw(self.screen)
            self.draw_ui()
        elif self.game_state == GAME_OVER:
            self.draw_game_over()
            
        pygame.display.flip()
        
    def draw_menu(self):
        """Отрисовывает главное меню игры."""
        title_font = pygame.font.SysFont('Arial', 44, bold=True)
        button_font = pygame.font.SysFont('Impact', 32)
        button_font1 = pygame.font.SysFont('Arial', 32)
        
        title = title_font.render("COSMOPOLITEN", True, WHITE)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
        
         # Рекорд
        record_text = button_font.render(f"рекорд: {self.record}", True, WHITE)
        self.screen.blit(record_text, (WIDTH // 2 - record_text.get_width() // 2, HEIGHT // 3))

        start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
        pygame.draw.rect(self.screen, LIGHT_BLUE, start_button, border_radius=10)

        start_text = button_font1.render("СТАРТ", True, BLACK)
        self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 10))
        
        # Кнопка Выход
        exit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
        pygame.draw.rect(self.screen, (200, 50, 50), exit_button, border_radius=10)
        exit_text = button_font1.render("ВЫХОД", True, WHITE)
        self.screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 80))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        if mouse_clicked:
            if start_button.collidepoint(mouse_pos):
                self.game_state = GAME
            elif exit_button.collidepoint(mouse_pos):
                self.running = False
    
    def draw_pause_screen(self):
        """Отрисовывает полупрозрачный экран паузы."""
        # Создаем полупрозрачную поверхность
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))  # Черный с прозрачностью 50%
        self.screen.blit(s, (0, 0))
        
        # Текст "ПАУЗА"
        font = pygame.font.SysFont('Arial', 72, bold=True)
        text = font.render("ПАУЗА", True, WHITE)
        self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
        
        # Подсказка
        small_font = pygame.font.SysFont('Arial', 24)
        hint = small_font.render("Нажмите ESC чтобы продолжить", True, WHITE)
        self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 50))    

    def draw_game_over(self):
        """Отрисовывает экран завершения игры."""
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        button_font = pygame.font.SysFont('Arial', 32)
        
        game_over_text = title_font.render("ИГРА ОКОНЧЕНА", True, WHITE)
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 4))
        
        score_text = button_font.render(f"Счет: {self.score}", True, WHITE)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 3))
        
        restart_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
        pygame.draw.rect(self.screen, LIGHT_BLUE, restart_button, border_radius=10)
        restart_text = button_font.render("ЗАНОВО", True, BLACK)
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))
        
        exit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 70, 200, 50)
        pygame.draw.rect(self.screen, (200, 50, 50), exit_button, border_radius=10)
        exit_text = button_font.render("ВЫХОД", True, WHITE)
        self.screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 80))

        # Обработка кликов
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        if mouse_clicked:
            if restart_button.collidepoint(mouse_pos):
                self.reset()
                self.game_state = GAME
            elif exit_button.collidepoint(mouse_pos):
                self.running = False
    
    def draw_ui(self):
        """Отрисовывает пользовательский интерфейс."""
        draw_text(self.screen, str(self.score), 18, WIDTH / 2, 10)
        
        # шкала здоровья
        health_pct = self.player.health
        fill_length = (health_pct / 100) * 100
        outline_rect = pygame.Rect(5, 5, 100, 10)
        fill_rect = pygame.Rect(5, 5, fill_length, 10)
        pygame.draw.rect(self.screen, WHITE, fill_rect)
        pygame.draw.rect(self.screen, BLUE, outline_rect, 2)
        
        # жизни игрока
        for i in range(self.player.hearts):
            img_rect = self.heart_img.get_rect()
            img_rect.x = WIDTH - 100 + 30 * i
            img_rect.y = 5
            self.screen.blit(self.heart_img, img_rect)
        
        # Отображение здоровья босса
        if self.boss_active:
            boss_text = f"BOSS: {'♥' * self.boss.health}"
            draw_text(self.screen, boss_text, 24, WIDTH // 2, 30)
        
        # Рекорд и текущий счет
        record_text = f"РЕКОРД: {self.record}"
        draw_text(self.screen, record_text, 18, 55 , 30)