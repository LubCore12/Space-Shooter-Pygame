import math

import pygame
from random import randint, uniform


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('../images/player.png').convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()

            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True
    
    def update(self, delta_time):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        is_collide_border = (self.rect.left < 0 or self.rect.right > WINDOW_WIDTH or
                             self.rect.top < 0 or self.rect.bottom > WINDOW_HEIGHT)

        if is_collide_border:
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > WINDOW_WIDTH:
                self.rect.right = WINDOW_WIDTH
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > WINDOW_HEIGHT:
                self.rect.bottom = WINDOW_HEIGHT
        else:
            self.direction = self.direction.normalize() if self.direction else self.direction

        self.rect.center += self.direction * self.speed * delta_time

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, all_sprites)
            laser_sound.play()

            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

        self.laser_timer()


class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))


class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)

        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, delta_time):
        self.rect.centery -= 750 * delta_time

        if pygame.sprite.spritecollide(self, meteor_sprites, True, pygame.sprite.collide_mask):
            self.kill()
            AnimatedExplosion(explosion_frames, self.rect.midtop, all_sprites)
            explosion_sound.play()

        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)

        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 2000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 500)
        self.angle = 0
        self.rotation_speed = randint(40, 85)

    def meteor_timer(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.start_time >= self.lifetime:
            self.kill()

    def update(self, delta_time):
        self.angle += (self.rotation_speed * delta_time) % 360

        self.rect.center += self.direction * self.speed * delta_time
        self.image = pygame.transform.rotate(self.original_surf, self.angle)
        self.rect = self.image.get_frect(center = self.rect.center)

        self.meteor_timer()


class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)

        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center = pos)

    def update(self, delta_time):
        self.frame_index += 35 * delta_time

        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]



def collisions():
    global running

    if pygame.sprite.spritecollide(player, meteor_sprites, False, pygame.sprite.collide_mask):
        running = False

def display_score():
    game_time = pygame.time.get_ticks() // 100
    text_surf = font.render(f'{game_time}', True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))

    pygame.draw.rect(display_surface, (240, 240, 240),
                     text_rect.inflate(25, 13).move(0, -5),
                     6, 12)

    display_surface.blit(text_surf, text_rect)


pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

pygame.display.set_caption('Space shooter')

running = True
clock = pygame.time.Clock()
font = pygame.font.Font('../font/Oxanium-Bold.ttf', 40)

all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()

explosion_frames = [pygame.image.load(f'../images/explosion/{i}.png').convert_alpha() for i in range(21)]

star_surf = pygame.image.load('../images/star.png').convert_alpha()

for i in range(20):
    Star(all_sprites, star_surf)

player = Player(all_sprites)

meteor_surf = pygame.image.load('../images/meteor.png').convert_alpha()
laser_surf = pygame.image.load('../images/laser.png').convert_alpha()

laser_sound = pygame.mixer.Sound('../audio/laser.wav')
laser_sound.set_volume(0.3)
explosion_sound = pygame.mixer.Sound('../audio/explosion.wav')
explosion_sound.set_volume(0.15)
game_music = pygame.mixer.Sound('../audio/game_music.wav')
game_music.set_volume(0.1)
game_music.play(loops = -1)

meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

while running:
    delta_time = clock.tick() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x = randint(0, WINDOW_WIDTH)
            y = randint(-100, 0)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    all_sprites.update(delta_time)

    collisions()

    display_surface.fill('#3a2e3f')
    all_sprites.draw(display_surface)
    display_score()

    pygame.display.update()

pygame.quit()