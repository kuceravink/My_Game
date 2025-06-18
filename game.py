import pygame
import random
from settings import *
from sprites import *

class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.load_data()
        self.reset()
        
    def load_data(self):
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
        self.all_sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.bust = pygame.sprite.Group()
        
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        for i in range(5):
            self.spawn_mob()
            
        self.score = 0
        self.game_state = MENU
        pygame.mixer.music.play(loops=-1)
        
    def spawn_mob(self):
        m = Mob(self)
        self.all_sprites.add(m)
        self.mobs.add(m)
        
    def run(self):
        self.running = True
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
    def update(self):
        if self.game_state == GAME:
            self.all_sprites.update()
            
            hits = pygame.sprite.groupcollide(self.mobs, self.bullets, True, True)
            for hit in hits:
                self.expl_sound.play()
                self.score += 50 - hit.radius
                expl = Explosion(self, hit.rect.center, 'bg')
                self.all_sprites.add(expl)
                self.spawn_mob()
                
                if random.random() > 0.9:
                    b = Bust(self, hit.rect.center)
                    self.all_sprites.add(b)
                    self.bust.add(b)
            
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
            
            hits = pygame.sprite.spritecollide(self.player, self.bust, True)
            for hit in hits:
                if hit.type == 'heart':
                    self.player.health = min(100, self.player.health + random.randrange(10, 30))
    
    def draw(self):
        self.screen.blit(self.background, self.background_rect)
        
        if self.game_state == MENU:
            self.draw_menu()
        elif self.game_state == GAME:
            self.all_sprites.draw(self.screen)
            self.draw_ui()
        elif self.game_state == GAME_OVER:
            self.draw_game_over()
            
        pygame.display.flip()
        
    def draw_menu(self):
        title_font = pygame.font.SysFont('Arial', 48, bold=True)
        button_font = pygame.font.SysFont('Arial', 32)
        
        title = title_font.render("COSMOPOLITEN", True, WHITE)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
        
        start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
        pygame.draw.rect(self.screen, LIGHT_BLUE, start_button, border_radius=10)
        start_text = button_font.render("СТАРТ", True, BLACK)
        self.screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 10))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        if mouse_clicked and start_button.collidepoint(mouse_pos):
            self.game_state = GAME
    
    def draw_game_over(self):
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
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        if mouse_clicked and restart_button.collidepoint(mouse_pos):
            self.reset()
            self.game_state = GAME
    
    def draw_ui(self):
        draw_text(self.screen, str(self.score), 18, WIDTH / 2, 10)
        
        # Health bar
        health_pct = self.player.health
        fill_length = (health_pct / 100) * 100
        outline_rect = pygame.Rect(5, 5, 100, 10)
        fill_rect = pygame.Rect(5, 5, fill_length, 10)
        pygame.draw.rect(self.screen, WHITE, fill_rect)
        pygame.draw.rect(self.screen, BLUE, outline_rect, 2)
        
        # Hearts
        for i in range(self.player.hearts):
            img_rect = self.heart_img.get_rect()
            img_rect.x = WIDTH - 100 + 30 * i
            img_rect.y = 5
            self.screen.blit(self.heart_img, img_rect)