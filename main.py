# inspired by https://github.com/russs123/brawler_tut
import pygame
from pygame import mixer

mixer.init()
pygame.init()

def load_img(path): return pygame.image.load(path).convert_alpha()
def anim_load(sprite_sheet, anim_steps, sprt_size, img_scale):
    anim_list = []
    for y, anim in enumerate(anim_steps):
        temp_img_list = []
        for x in range(anim):
            temp_img = sprite_sheet.subsurface(x * sprt_size, y * sprt_size, sprt_size, sprt_size)
            temp_img_list.appeng(pygame.transform.scale(temp_img, (sprt_size * img_scale, sprt_size * img_scale)))
        anim_list.append(temp_img_list)
    return anim_list

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

FPS = 60

RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SPEED = 10
GRAVITY = 2


background_img = load_img("assets/farm.png")

PATRICK_SIZE = 81
PATRICK_SCALE = 2
PATRICK_OFFSET = [36, 28]
PATRICK_DATA = [PATRICK_SIZE, PATRICK_SCALE, PATRICK_OFFSET]
FRODO_DATA = PATRICK_DATA


class Fighter:
    def __init__(self, fightNum, x, y, flip, data, sprite_sheet, anim_steps, attack_sfx):
        self.fighter_num = fightNum
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = anim_load(sprite_sheet, anim_steps, self.size, self.image_scale)
        self.action = 0 #0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.hit = False
        self.health = 100
        self.alive = True
        self.attack_sound = attack_sfx

    def move(self, screen_width, screen_height, surface, target, is_round_over):
        dx, dy = 0, 0
        self.running = False
        self.attack_type = 0

        key = pygame.key.get_pressed()

        if not self.attacking and self.alive and not is_round_over:
            if self.fighter_num == 1:
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2

            elif self.fighter_num == 2:
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)#6:death
        elif self.hit == True:
            self.update_action(5)#5:hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)#3:attack1
            elif self.attack_type == 2:
                self.update_action(4)#4:attack2
        elif self.jump == True:
            self.update_action(2)#2:jump
        elif self.running == True:
            self.update_action(1)#1:run
        else:
            self.update_action(0)#0:idle

        anim_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > anim_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            #self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update_action(self, new_act):
        if new_act != self.action:
            self.action = new_act
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))

class FighterManager:
    def __init__(self, game):
        self.game = game
        #self.game.sound_player.add_sound("patrick_sfx", 0.5, "assets/patrick_sfx.wav"); patrick_sfx = self.game.sound_player.get_sound("patrick_sfx")
        #self.game.sound_player.add_sound("frodo_sfx", 0.5, "assets/frodo_sfx.wav"); frodo_sfx = self.game.sound_player.get_sound("frodo_sfx")
        
        self.fighterL = Fighter(1, 200, 310, False, PATRICK_DATA, patrick_sheet, PATRICK_ANIM_STEPS, None)#patrick_sfx)
        self.fighterR = Fighter(2, 700, 310, True, FRODO_DATA, frodo_sheet, FRODO_ANIM_STEPS, None)#frodo_sfx)
        self.hbar_width = round((SCREEN_WIDTH * 0.9) / 2)

    def draw_health_bar(self, amnt, x, y):
        val = amnt / 100
        pygame.draw.rect(game.screen, WHITE, (x - 2, y - 2, self.hbar_width + 4, 34))
        pygame.draw.rect(game.screen, RED, (x, y, self.hbar_width, 30))
        pygame.draw.rect(game.screen, YELLOW, (x, y, self.hbar_width * val, 30))

    def update(self):
        self.draw_health_bar(self.fighterL.health, SCREEN_WIDTH + 20, 20)
        self.draw_health_bar(self.fighterR.health, SCREEN_WIDTH // 2 + 80, 20)

        self.fighterL.move(SCREEN_WIDTH, SCREEN_HEIGHT, game.screen, self.fighterR, game.round_over)
        self.fighterR.move(SCREEN_WIDTH, SCREEN_HEIGHT, game.screen, self.fighterL, game.round_over)

        self.fighterL.update()
        self.fighterR.update()
        self.fighterL.draw(game.screen)
        self.fighterR.draw(game.screen)

class SoundPlayer:
    def __init__(self):
        self.sounds = {}
    def play_music(self, musicPath, vol = 0.5, loops = -1, start = 0.0, fade_ms = 5000):
        pygame.mixer.music.load(musicPath)
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.play(loops, start, fade_ms)
    def add_sound(self, sound_name, vol, path):
        new_sound = pygame.mixer.Sound(path)
        new_sound.set_volume(vol)
        self.sounds[sound_name] = new_sound
    def get_sound(self, sound_name):
        return self.sounds.get(sound_name)
    def play(self, sound_name):
        self.sounds[sound_name].play()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Fight Farm")
        self.clock = pygame.time.Clock()
        self.sound_player = SoundPlayer()
        self.fight_manager = FighterManager(self)
        self.round_over = False
    def draw_text(self, text, font, text_col, x, y):
        txt_rendered = font.render(text, True, text_col)
        self.screen.blit(txt_rendered, (x, y))
    def run(self):
        def draw_background():
            scaled_background = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(scaled_background, (0, 0))

        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            draw_background()
            self.fight_manager.update()

            pygame.display.update()


game = Game()
game.run()

pygame.quit()