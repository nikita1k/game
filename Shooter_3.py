import pygame
import sys
import os
import random
import csv

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

def start_game_play():
    screen.fill(BG)
    screen.blit(start_img, ((SCREEN_WIDTH - start_img.get_width()) // 2, 120))
    screen.blit(start_img, ((SCREEN_WIDTH - start_img.get_width()) // 2, 220))
    screen.blit(exit_img, ((SCREEN_WIDTH - exit_img.get_width()) // 2, 320))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

def end():
    global level, MAX_LEVELS, world_data, bg_scroll, start_game, get_level, play, pause, TIME
    screen.blit(end_img, ((SCREEN_WIDTH - end_img.get_width()) // 2, (SCREEN_HEIGHT - end_img.get_height()) // 2))
    if restart_end_button.draw(screen):
        world_data = reset_level()
        bg_scroll = 0
        get_level = True
        play = True
    elif sistem_end_button.draw(screen):
        world_data = reset_level()
        bg_scroll = 0
        start_game = True
        start_player = True
        get_level = True
        play = False
    elif player.alive:
        if sistem1_end_button.draw(screen):
            if pause:
                return True
            world_data = reset_level()
            bg_scroll = 0
            level += 1
            if level <= MAX_LEVELS:
                get_level = True
                play = True
            else:
                level -= 1
    if not pause:
        if not player.alive:
            TIME = 0
            screen.blit(gameover_img, ((SCREEN_WIDTH - end_img.get_width()) // 2 + (end_img.get_width() - gameover_img.get_width()) // 2, end_img.get_height() - 2 * gameover_img.get_height()))
            return
        draw_text('RESULTS', font, WHITE, (SCREEN_WIDTH - end_img.get_width()) // 2 + 105, SCREEN_HEIGHT - end_img.get_height() - 25)
        text = [player.max_health, player.health, player.kill, 25, 'MAX HP', 'YOU HP', 'KILL', 'TIME']
        for y in range(len(text) // 2):
            draw_text(str(text[y + len(text) // 2]), font, WHITE, (SCREEN_WIDTH - end_img.get_width()) // 2, SCREEN_HEIGHT - end_img.get_height() + 25 * y)
            draw_text(str(text[y]), font, WHITE, (SCREEN_WIDTH - end_img.get_width()) * 2 // 3 + 25, SCREEN_HEIGHT - end_img.get_height() + 25 * y)
        #draw_text('end', font, WHITE, SCREEN_WIDTH - end_img.get_width(), SCREEN_HEIGHT - end_img.get_height() + 25 * y + 1)
    else:
        screen.blit(pause_img, ((SCREEN_WIDTH - end_img.get_width()) // 2 + (end_img.get_width() - pause_img.get_width()) // 2, end_img.get_height() - 2 * pause_img.get_height()))


class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, max_health, pover_jump, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.kill = 0
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.max_health = max_health
        self.health = max_health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.pover_jump = pover_jump
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.vision1 = pygame.Rect(0, 0, 15, 20)
        self.idling = False
        self.idling_counter = 0
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left and not moving_right:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right and not moving_left:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and not self.in_air:
            self.vel_y = -self.pover_jump
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom


        if pygame.sprite.spritecollide(self, water_group, False):
            self.health -= 5
            self.jump = True
            self.in_air = False

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0


        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete



    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1

    def hit(self):
        for i in range(-2, 3):
            hit_0 = Hit(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), 5 * i + self.rect.centery, self.direction)
            hit_group.add(hit_0)


    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            if self.vision1.colliderect(player.rect):
                self.update_action(0)
                self.hit()
            elif self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    self.vision1.center = (self.rect.centerx + 5 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll


    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN == 100:
            self.update_time = pygame.time.get_ticks()
            if self.action == 3 and self.frame_index == len(self.animation_list[self.action]) - 1:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = (self.frame_index + 1) % len(self.animation_list[self.action])



    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()



    def check_alive(self):
        if self.health < 1:
            if self.alive and self.char_type == 'enemy':
                player.kill += 1
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, MAX_HP, PAWER_JUMP, SPEED, BULLET, GRENADE)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 100, 0, 2, 2000, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar


    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()


class Hit(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.cooldown = 5

    def update(self):
        self.cooldown -= 1
        if self.cooldown == 0:
            self.kill()
        if pygame.sprite.spritecollide(player, hit_group, False):
            if player.alive:
                player.health -= 0.1
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, hit_group, False):
                if enemy.alive:
                    enemy.health -= 5



class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom 


        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0


    def update(self):
        #scroll
        self.rect.x += screen_scroll

        EXPLOSION_SPEED = 4
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


if __name__ == '__main__':
    pygame.init()

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('run jump shoot')

    clock = pygame.time.Clock()
    clock_game = pygame.time.Clock()
    FPS = 60

    GRAVITY = 0.75
    SCROLL_THRESH = 200
    ROWS = 16
    COLS = 150
    TILE_SIZE = SCREEN_HEIGHT // ROWS
    TILE_TYPES = 21
    MAX_LEVELS = 2
    screen_scroll = 0
    bg_scroll = 0
    experience = 0
    
    f = open("player.txt", encoding="utf8")
    for _ in range(6):
        row = f.readline().split()
        if 'MAX_HP' == row[0]:
            MAX_HP = int(row[-1])
        if 'SPEED' == row[0]:
            SPEED = int(row[-1])
        if 'PAWER_JUMP' == row[0]:
            PAWER_JUMP = int(row[-1])
        if 'PAWER' == row[0]:
            PAWER = int(row[-1])
        if 'BULLET' == row[0]:
            BULLET = int(row[-1])
        if 'GRENADE' == row[0]:
            GRENADE = int(row[-1])
    f.close()
    start_game = True
    start_player = False
    play = False
    new_game = True
    pause = False
    
    draw_text_x = SCREEN_WIDTH // 3
    draw_text_y = 150
    
    BG = (144, 201, 120)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)

    moving_left = False
    moving_right = False
    shoot = False
    grenade = False
    grenade_thrown = False
    hit = False

    start_img = pygame.image.load('img/start.png').convert_alpha()
    exit_img = pygame.image.load('img/exit.png').convert_alpha()
    restart_img = pygame.image.load('img/restart.png').convert_alpha()
    sistem_img = pygame.image.load('img/sistem.png').convert_alpha()
    plus_img = pygame.image.load('img/plus.png').convert_alpha()
    minys_img = pygame.image.load('img/minys.png').convert_alpha()
    level_1_img = pygame.image.load('img/level_1.png').convert_alpha()
    level_2_img = pygame.image.load('img/level_2.png').convert_alpha()
    level_3_img = pygame.image.load('img/level_3.png').convert_alpha()
    end_img = pygame.image.load('img/end.png').convert_alpha()
    pause_img = pygame.image.load('img/pause.png').convert_alpha()
    next_img = pygame.image.load('img/next.png').convert_alpha()
    gameover_img = pygame.image.load('img/gameover.png').convert_alpha()
    
    pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
    pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
    mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
    sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
    
    img_list = []
    for x in range(TILE_TYPES):
        img = pygame.image.load(f'img/Tile/{x}.png')
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)
        
    bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
    grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
    health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
    ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
    grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
    item_boxes = {
        'Health'    : health_box_img,
        'Ammo'      : ammo_box_img,
        'Grenade'   : grenade_box_img
    }

    font = pygame.font.SysFont('Futura', 30)

    start_button = Button(SCREEN_WIDTH // 2 - start_img.get_width() // 2, SCREEN_HEIGHT // 2 - start_img.get_height() - 75, start_img, 1)
    start_in_player_button = Button(SCREEN_WIDTH // 2 - start_img.get_width() - 20, SCREEN_HEIGHT // 2 - start_img.get_height() + 150, start_img, 1)
    exit_button = Button(SCREEN_WIDTH // 2 - exit_img.get_width() // 2, SCREEN_HEIGHT // 2 - exit_img.get_height() + 75, exit_img, 1)
    restart_button = Button(SCREEN_WIDTH // 2 + 75, SCREEN_HEIGHT // 2 + 50, restart_img, 1)
    sistem_button = Button(SCREEN_WIDTH // 2 - sistem_img.get_width() // 2, SCREEN_HEIGHT // 2 - sistem_img.get_height(), sistem_img, 1)
    sistem_in_game_button = Button(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 + 50, sistem_img, 1)
    
    restart_end_button = Button((SCREEN_WIDTH - end_img.get_width()) // 2 - restart_img.get_width() // 2, end_img.get_height() + restart_img.get_height(), restart_img, 1)
    sistem_end_button = Button((SCREEN_WIDTH - end_img.get_width()) // 2 + (end_img.get_width() - sistem_img.get_width()) // 2, end_img.get_height() + sistem_img.get_height(), sistem_img, 1)
    sistem1_end_button = Button((SCREEN_WIDTH - end_img.get_width()) // 2 + end_img.get_width() - (sistem_img.get_width()) // 2, end_img.get_height() + sistem_img.get_height(), next_img, 1)
    
    plus_button_HP = Button(draw_text_x + 135, draw_text_y + 25 * 1, plus_img, 1)
    minys_button_HP = Button(draw_text_x - 35, draw_text_y + 25 * 1, minys_img, 1)
    plus_button_SPEED = Button(draw_text_x + 135, draw_text_y + 25 * 3, plus_img, 1)
    minys_button_SPEED = Button(draw_text_x - 35, draw_text_y + 25 * 3, minys_img, 1)
    plus_button_PAWER_JUMP = Button(draw_text_x + 135, draw_text_y + 25 * 5, plus_img, 1)
    minys_button_PAWER_JUMP = Button(draw_text_x - 35, draw_text_y + 25 * 5, minys_img, 1)
    plus_button_PAWER = Button(draw_text_x + 135, draw_text_y + 25 * 7, plus_img, 1)
    minys_button_PAWER = Button(draw_text_x - 35, draw_text_y + 25 * 7, minys_img, 1)
    plus_button_GRENADE = Button(draw_text_x + 135, draw_text_y + 25 * 9, plus_img, 1)
    minys_button_GRENADE = Button(draw_text_x - 35, draw_text_y + 25 * 9, minys_img, 1)

    level_1_button = Button(SCREEN_WIDTH // 2 * 1 // 3 + SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2 - level_1_img.get_height() // 2, level_1_img, 1)
    level_2_button = Button(SCREEN_WIDTH // 2 * 2 // 3 + SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2 - level_2_img.get_height() // 2, level_2_img, 1)
    level_3_button = Button(SCREEN_WIDTH // 2 * 3 // 3 + SCREEN_WIDTH // 6, SCREEN_HEIGHT // 2 - level_3_img.get_height() // 2, level_3_img, 1)

    enemy_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    hit_group = pygame.sprite.Group()
    grenade_group = pygame.sprite.Group()
    explosion_group = pygame.sprite.Group()
    item_box_group = pygame.sprite.Group()
    decoration_group = pygame.sprite.Group()
    water_group = pygame.sprite.Group()
    exit_group = pygame.sprite.Group()

    run = True
    clock_game.tick()
    while run:
        clock.tick(FPS)
        #print(pause)

        if start_game:
            screen.fill(BG)
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if start_button.draw(screen):
                start_game = False
                get_level = True
            if sistem_button.draw(screen):
                start_game = False
                start_player = True
            if exit_button.draw(screen):
                run = False
        elif start_player:
            screen.fill(BG)
            draw_text(f'EXPERIENCE', font, WHITE, draw_text_x, draw_text_y + 25 * -2)
            draw_text(f'{experience}', font, WHITE, draw_text_x + 150, draw_text_y + 25 * -2) # 25
            draw_text(f'HP', font, WHITE, draw_text_x, draw_text_y + 25 * 0) # 25
            draw_text(f'{MAX_HP}', font, WHITE, draw_text_x, draw_text_y + 25 * 1) # 25
            draw_text(f'SPEED ', font, WHITE, draw_text_x, draw_text_y + 25 * 2)
            draw_text(f'{SPEED} ', font, WHITE, draw_text_x, draw_text_y + 25 * 3)
            draw_text(f'PAWER JUMP', font, WHITE, draw_text_x, draw_text_y + 25 * 4)
            draw_text(f'{PAWER_JUMP}', font, WHITE, draw_text_x, draw_text_y + 25 * 5)
            draw_text(f'PAWER', font, WHITE, draw_text_x, draw_text_y + 25 * 6)
            draw_text(f'{PAWER}', font, WHITE, draw_text_x, draw_text_y + 25 * 7)
            draw_text(f'GRENADE', font, WHITE, draw_text_x, draw_text_y + 25 * 8)
            draw_text(f'{GRENADE}', font, WHITE, draw_text_x, draw_text_y + 25 * 9)
            if plus_button_HP.draw(screen) and experience > 0:
                MAX_HP += 5
                experience -= 1
                if MAX_HP >= 250:
                    MAX_HP = 250
            elif minys_button_HP.draw(screen):
                MAX_HP -= 5
                experience += 1
                if MAX_HP <= 100:
                    MAX_HP = 100
            elif plus_button_SPEED.draw(screen) and experience > 0:
                SPEED += 1
                experience -= 1
                if SPEED >= 10:
                    SPEED = 10
            elif minys_button_SPEED.draw(screen):
                SPEED -= 1
                experience += 1
                if SPEED <= 5:
                    SPEED = 5
            elif plus_button_PAWER_JUMP.draw(screen) and experience > 0:
                PAWER_JUMP += 2
                experience -= 1
                if PAWER_JUMP >= 21:
                    PAWER_JUMP = 21
            elif minys_button_PAWER_JUMP.draw(screen):
                PAWER_JUMP -= 2
                experience += 1
                if PAWER_JUMP <= 11:
                    PAWER_JUMP = 11
            elif plus_button_PAWER.draw(screen) and experience > 0:
                PAWER += 5
                experience -= 1
                if PAWER >= 50:
                    PAWER = 50
            elif minys_button_PAWER.draw(screen):
                PAWER -= 5
                experience += 1
                if PAWER <= 10:
                    PAWER = 2
            elif plus_button_GRENADE.draw(screen) and experience > 0:
                GRENADE += 2
                experience -= 1
                if GRENADE >= 10:
                    GRENADE = 10
            elif minys_button_GRENADE.draw(screen):
                GRENADE -= 2
                experience += 1
                if GRENADE <= 2:
                    GRENADE = 2
            if start_in_player_button.draw(screen):
                info_player = [['MAX_HP', '=', str(MAX_HP)],
                               ['SPEED', '=', str(SPEED)],
                               ['PAWER_JUMP', '=', str(PAWER_JUMP)],
                               ['PAWER', '=', str(PAWER)],
                               ['BULLET', '=', str(BULLET)],
                               ['GRENADE', '=', str(GRENADE)]]
                f = open("player.txt", 'w')
                for write in info_player:
                    f.write(' '.join(write))
                    f.write('\n')
                f.close()
                start_player = False
                get_level = True
        elif get_level:
            screen.fill(BLACK)
            if level_1_button.draw(screen):
                level = 1
                play = True
            elif level_2_button.draw(screen):
                level = 2
                play = True
            elif level_3_button.draw(screen):
                level = 3
                play = True
            if play:
                world_data = []
                for row in range(ROWS):
                    r = [-1] * COLS
                    world_data.append(r)
                f = open(f"level{level}_data.txt", encoding="utf8")
                for x in range(16):
                    for y, tile in enumerate(f.readline().split(',')):
                        world_data[x][y] = int(tile)
                f.close()
                world = World()
                player, health_bar = world.process_data(world_data)
                get_level = False
                play = False
        elif pause:
            if end():
                pause = False
        else:
            if not pygame.display.get_active():# or pause_button.draw(screen):
                pause = True
            if new_game:
                new_game = False
                clock_game.tick()
            draw_bg()
            world.draw()
            health_bar.draw(player.health)
            draw_text(f'AMMO: {player.ammo}', font, WHITE, 10, 35)
            draw_text(f'GRENADE: {player.grenades}', font, WHITE, 10, 60)
            draw_text('AMMO:', font, WHITE, 10, 35)
            '''draw_text('AMMO: ', font, WHITE, 10, 35)
            for x in range(player.ammo):
                screen.blit(bullet_img, (90 + (x * 10), 40))
            #show grenades
            draw_text('GRENADES: ', font, WHITE, 10, 60)
            for x in range(player.grenades):
                screen.blit(grenade_img, (135 + (x * 15), 60))'''


            player.update()
            player.draw()

            for enemy in enemy_group:
                enemy.ai()
                enemy.update()
                enemy.draw()

            bullet_group.update()
            bullet_group.draw(screen)
            hit_group.update()
            hit_group.draw(screen)
            grenade_group.update()
            grenade_group.draw(screen)
            explosion_group.update()
            explosion_group.draw(screen)
            item_box_group.update()
            item_box_group.draw(screen)
            decoration_group.update()
            decoration_group.draw(screen)
            water_group.update()
            water_group.draw(screen)
            exit_group.update()
            exit_group.draw(screen)

            if player.alive:
                if shoot:
                    player.shoot()
                elif grenade and not grenade_thrown and player.grenades > 0:
                    grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                                player.rect.top, player.direction)
                    grenade_group.add(grenade)
                    player.grenades -= 1
                    grenade_thrown = True
                elif hit:
                    player.hit()
                    hit = False
                if player.in_air:
                    player.update_action(2)
                elif moving_left or moving_right:
                    player.update_action(1)
                else:
                    player.update_action(0)
                screen_scroll, level_complete = player.move(moving_left, moving_right)
                bg_scroll -= screen_scroll
                if level_complete:
                    experience = player.kill
                    if clock_game.tick() // 1000 > 1:
                        TIME = clock_game.tick() // 1000
                    end()
            else:
                end()
                screen_scroll = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_SPACE:
                    shoot = True
                if event.key == pygame.K_q:
                    grenade = True
                if event.key == pygame.K_e:
                    hit = True
                if event.key == pygame.K_w and player.alive:
                    player.jump = True
                if event.key == pygame.K_ESCAPE:
                    run = False


            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_SPACE:
                    shoot = False
                if event.key == pygame.K_q:
                    grenade = False
                    grenade_thrown = False


        pygame.display.update()

pygame.quit()
