import pygame
import math
import sys
import time

# init
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.init()

game_running = True
MAX_FPS = 900
dt_tickrate = 60
draw_graph = 0
width = pygame.display.Info().current_w
height = pygame.display.Info().current_h
screen = pygame.display.set_mode(
    (width, height), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
clock = pygame.time.Clock()


last_time = time.time()

all_objects_width = 2000
all_objects_height = 2000
all_objects = pygame.Surface((all_objects_width, all_objects_height))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (7, 31, 41)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

movement_buttons = [0, 0, 0, 0]  # a, w, d, s
font_retro_gaming_25 = pygame.font.Font("data/fonts/Retro_Gaming.ttf", 25)

# sprites


class Flat(pygame.sprite.Sprite):
    def __init__(self, flat_hitbox_image, flat_image, flat_image_overlay):
        pygame.sprite.Sprite.__init__(self)
        self.flat_hitbox_image = flat_hitbox_image
        self.flat_image = flat_image
        self.flat_image_overlay = flat_image_overlay

    def update_collide_mask(self, center_cords, square_size):
        cropped = pygame.Surface((square_size * 3, square_size * 3))
        cropped.fill(WHITE)
        cropped.set_colorkey(WHITE)
        cropped.blit(
            self.flat_hitbox_image,
            (0,
             0),
            (center_cords[0] -
             square_size,
             center_cords[1] -
             square_size,
             center_cords[0] +
             square_size *
             2,
             center_cords[1] +
             square_size *
             2))

        self.image = cropped
        self.rect = pygame.Rect(
            (center_cords[0] - square_size,
             center_cords[1] - square_size,
             self.image.get_width(),
             self.image.get_height()))
        self.mask = pygame.mask.from_surface(cropped)


class Player(pygame.sprite.Sprite):
    def __init__(
            self,
            cords,
            player_rect_image,
            speed_linear,
            change_animation_delay,
            animation_images):
        pygame.sprite.Sprite.__init__(self)
        self.x = cords[0]
        self.y = cords[1]
        self.player_rect_image = player_rect_image
        self.last_direction = 0
        self.speed_linear = speed_linear
        self.speed_diagonal = round(math.sqrt((self.speed_linear**2) // 2))
        self.current_speed = 0
        self.last_change_animation = time.time()
        self.change_animation_delay = change_animation_delay
        self.animation_state = 1
        self.animation_images = animation_images

        self.image = self.player_rect_image
        self.mask = pygame.mask.from_surface(self.player_rect_image)
        temp_mask_size = self.mask.get_size()
        self.rect = (self.x, self.y, temp_mask_size[0], temp_mask_size[1])

    def update_collide_mask(self):
        self.mask = pygame.mask.from_surface(self.player_rect_image)
        temp_mask_size = self.mask.get_size()
        self.rect = (self.x, self.y, temp_mask_size[0], temp_mask_size[1])

    def update_animation_state(self):
        if (time.time() - self.last_change_animation) > self.change_animation_delay:
            self.animation_state = (1 - (self.animation_state - 1)) + 1
            self.last_change_animation = time.time()

    def draw(self):
        temp_x_draw = self.x
        temp_y_draw = self.y - 35
        if movement_buttons.count(1) == 0:
            if self.last_direction == 0:
                all_objects.blit(
                    self.animation_images["image_left"], (temp_x_draw, temp_y_draw))
            if self.last_direction == 1:
                all_objects.blit(
                    self.animation_images["image_top"], (temp_x_draw, temp_y_draw))
            if self.last_direction == 2:
                all_objects.blit(
                    self.animation_images["image_right"], (temp_x_draw, temp_y_draw))
            if self.last_direction == 3:
                all_objects.blit(
                    self.animation_images["image_down"], (temp_x_draw, temp_y_draw))
        else:
            direction = 0
            for i in range(len(movement_buttons)):
                if movement_buttons[i] == 1:
                    direction = i
                    break
            if direction == 0:
                exec('all_objects.blit(self.animation_images["image_left_' + str(
                    self.animation_state) + '"], (temp_x_draw, temp_y_draw))')
            if direction == 1:
                exec('all_objects.blit(self.animation_images["image_top_' + str(
                    self.animation_state) + '"], (temp_x_draw, temp_y_draw))')
            if direction == 2:
                exec('all_objects.blit(self.animation_images["image_right_' + str(
                    self.animation_state) + '"], (temp_x_draw, temp_y_draw))')
            if direction == 3:
                exec('all_objects.blit(self.animation_images["image_down_' + str(
                    self.animation_state) + '"], (temp_x_draw, temp_y_draw))')

    def check_collide(self, flat):
        temp_collide = False

        if pygame.sprite.collide_mask(self, flat):
            temp_collide = True
        return temp_collide

    def update_position(self, dt, flat):
        self.current_speed = 0
        if movement_buttons.count(1) == 1:
            self.current_speed = self.speed_linear
        elif movement_buttons.count(1) > 1:
            self.current_speed = self.speed_diagonal
        self.current_speed = math.ceil(self.current_speed * dt)

        if movement_buttons[0]:
            for i in range(self.current_speed):
                self.x -= 1
                self.update_collide_mask()
                if self.check_collide(flat):
                    self.x += 1
                    break
            self.last_direction = 0
        if movement_buttons[1]:
            for i in range(self.current_speed):
                self.y -= 1
                self.update_collide_mask()
                if self.check_collide(flat):
                    self.y += 1
                    break
            self.last_direction = 1
        if movement_buttons[2]:
            for i in range(self.current_speed):
                self.x += 1
                self.update_collide_mask()
                if self.check_collide(flat):
                    self.x -= 1
                    break
            self.last_direction = 2
        if movement_buttons[3]:
            for i in range(self.current_speed):
                self.y += 1
                self.update_collide_mask()
                if self.check_collide(flat):
                    self.y -= 1
                    break
            self.last_direction = 3


class Bonfire(pygame.sprite.Sprite):
    def __init__(
            self,
            cords,
            rect_image,
            change_animation_delay,
            animation_images,
            glow_image):
        self.x = cords[0]
        self.y = cords[1]
        self.rect_image = rect_image
        self.change_animation_delay = change_animation_delay
        self.last_change_animation = time.time()
        self.animation_images = animation_images
        self.glow_image = glow_image
        self.animation_state = 0

        self.image = self.rect_image
        self.mask = pygame.mask.from_surface(self.rect_image)
        temp_mask_size = self.mask.get_size()
        self.rect = (self.x, self.y, temp_mask_size[0], temp_mask_size[1])

    def update_collide_mask(self):
        self.image = self.rect_image
        self.mask = pygame.mask.from_surface(self.rect_image)
        temp_mask_size = self.mask.get_size()
        self.rect = (self.x, self.y, temp_mask_size[0], temp_mask_size[1])

    def update_animation_state(self):
        if (time.time() - self.last_change_animation) > self.change_animation_delay:
            if self.animation_state == 3:
                self.animation_state = 0
                self.last_change_animation = time.time()
            else:
                self.animation_state = self.animation_state + 1
                self.last_change_animation = time.time()

    def check_entering_in_fire_zone(self, player, optical_flare_borders):
        temp_how_far = how_far(player.x, player.y, self.x, self.y)
        return (
            temp_how_far < optical_flare_borders[1] and temp_how_far > optical_flare_borders[0],
            temp_how_far)

    def draw(self):
        temp_fire_image = self.animation_images["bonfire_" +
                                                str(self.animation_state)]
        all_objects.blit(temp_fire_image,
                         (self.x - (temp_fire_image.get_width() // 2),
                          self.y - (temp_fire_image.get_height() // 2)))


class Text(pygame.sprite.Sprite):
    def __init__(
            self,
            text,
            size,
            cords,
            animation_duration,
            show_text,
            color=WHITE):
        self.x = cords[0]
        self.y = cords[1]
        self.animation_duration = animation_duration
        self.show_text = show_text
        self.last_state_change_time = -animation_duration
        self.image = pygame.font.Font(
            "data/fonts/Retro_Gaming.ttf",
            size).render(
            text,
            True,
            color)

    def draw(self):
        if self.show_text:
            if (time.time() - self.last_state_change_time) < self.animation_duration:
                self.image.set_alpha(
                    (time.time() -
                     self.last_state_change_time) *
                    round(
                        255 /
                        self.animation_duration))
                all_objects.blit(self.image, (self.x, self.y))
            else:
                self.image.set_alpha(255)
                all_objects.blit(self.image, (self.x, self.y))
        else:
            if time.time() - self.last_state_change_time < self.animation_duration:
                self.image.set_alpha(255 -
                                     (time.time() -
                                      self.last_state_change_time) *
                                     math.floor(256 /
                                                self.animation_duration))
                all_objects.blit(self.image, (self.x, self.y))
            elif self.image.get_alpha() > 0:
                self.image.set_alpha(0)

    def hide(self):
        self.show_text = 0
        self.last_state_change_time = time.time()

    def show(self):
        self.show_text = 1
        self.last_state_change_time = time.time()


# create map
flat = Flat(pygame.image.load("data/flat_hitbox.png").convert_alpha(),
            pygame.image.load("data/flat_image.png").convert_alpha(),
            pygame.image.load("data/flat_image_overlay.png").convert_alpha())

# create player
player_animation_images = dict()
player_animation_images["image_left"] = pygame.image.load(
    "data/player_animations/left.png").convert_alpha()
player_animation_images["image_left_1"] = pygame.image.load(
    "data/player_animations/left_1.png").convert_alpha()
player_animation_images["image_left_2"] = pygame.image.load(
    "data/player_animations/left_2.png").convert_alpha()
player_animation_images["image_right"] = pygame.image.load(
    "data/player_animations/right.png").convert_alpha()
player_animation_images["image_right_1"] = pygame.image.load(
    "data/player_animations/right_1.png").convert_alpha()
player_animation_images["image_right_2"] = pygame.image.load(
    "data/player_animations/right_2.png").convert_alpha()
player_animation_images["image_down"] = pygame.image.load(
    "data/player_animations/down.png").convert_alpha()
player_animation_images["image_down_1"] = pygame.image.load(
    "data/player_animations/down_1.png").convert_alpha()
player_animation_images["image_down_2"] = pygame.image.load(
    "data/player_animations/down_2.png").convert_alpha()
player_animation_images["image_top"] = pygame.image.load(
    "data/player_animations/top.png").convert_alpha()
player_animation_images["image_top_1"] = pygame.image.load(
    "data/player_animations/top_1.png").convert_alpha()
player_animation_images["image_top_2"] = pygame.image.load(
    "data/player_animations/top_2.png").convert_alpha()
player = Player((500, 1200), pygame.image.load(
    "data/player_hitbox.png").convert_alpha(), 4, 0.175, player_animation_images)
offset_x = -player.x
offset_y = -player.y

# create bonfires
glow_image = pygame.image.load("data/glow/glow.png").convert_alpha()
bonfire_animation_images = dict()
bonfire_animation_images["bonfire_0"] = pygame.image.load(
    "data/bonfire/bonfire_0.png").convert_alpha()
bonfire_animation_images["bonfire_1"] = pygame.image.load(
    "data/bonfire/bonfire_1.png").convert_alpha()
bonfire_animation_images["bonfire_2"] = pygame.image.load(
    "data/bonfire/bonfire_2.png").convert_alpha()
bonfire_animation_images["bonfire_3"] = pygame.image.load(
    "data/bonfire/bonfire_3.png").convert_alpha()
bonfire_1 = Bonfire(
    (880,
     1000),
    pygame.image.load("data/bonfire_hitbox.png").convert_alpha(),
    0.2,
    bonfire_animation_images,
    glow_image)
bonfire_2 = Bonfire(
    (200,
     1240),
    pygame.image.load("data/bonfire_hitbox.png").convert_alpha(),
    0.2,
    bonfire_animation_images,
    glow_image)

# create text
text_greeting = Text(
    "Привет! Сейчас ты увидишь некоторые возможности pygame!",
    24,
    (50,
     1100),
    2,
    1)
text_optical_flares = Text(
    "Подойдёшь к огню - увидишь блики в камере!", 24, (70, 1000), 2, 0)

# optical flares elements
star_image = pygame.image.load("data/glow/star.png").convert_alpha()
glow_rounds_image = pygame.image.load(
    "data/glow/glow_rounds.png").convert_alpha()
rainbow_rounds_image = pygame.image.load(
    "data/glow/rainbow_rounds.png").convert_alpha()
glass_image = pygame.image.load("data/glow/glass.png").convert_alpha()
draw_optical_flare = 0
optical_flare_distance = 9999999999
optical_flare_borders = [0, 200]

step_sound = pygame.mixer.Sound("data/sounds/step.ogg")
step_sound.set_volume(0.03)
step_sound_duration_last_played = 0
step_sound_duration = 0.5

fire_burning_sound = pygame.mixer.Sound("data/sounds/burning_fire.ogg")
fire_burning_sound.set_volume(0)
fire_burning_channel = fire_burning_sound.play(-1)


# event
def event(i):
    global game_running
    if i.type == pygame.QUIT:
        game_running = False
    if i.type == pygame.KEYDOWN:
        if i.key == pygame.K_a:
            movement_buttons[0] = 1
        if i.key == pygame.K_w:
            movement_buttons[1] = 1
        if i.key == pygame.K_d:
            movement_buttons[2] = 1
        if i.key == pygame.K_s:
            movement_buttons[3] = 1
    if i.type == pygame.KEYUP:
        if i.key == pygame.K_a:
            movement_buttons[0] = 0
        if i.key == pygame.K_w:
            movement_buttons[1] = 0
        if i.key == pygame.K_d:
            movement_buttons[2] = 0
        if i.key == pygame.K_s:
            movement_buttons[3] = 0


# process logic
def how_far(x1, y1, x2, y2):
    temp_a = x1 - x2
    temp_b = y1 - y2
    temp_c = math.sqrt(temp_a * temp_a + temp_b * temp_b)
    return temp_c


def process_logic():
    global offset_x, offset_y, temp_entering_in_fire_zones, \
        draw_optical_flare, optical_flare_distance, temp_flare_x_from, \
        temp_flare_y_from, bonfires, last_time, dt
    temp_player_x = player.x
    temp_player_y = player.y

    dt = (time.time() - last_time) * dt_tickrate
    last_time = time.time()

    flat.update_collide_mask((player.x, player.y), player.image.get_width())

    temp_entering_in_fire_zones = 0
    bonfires = [bonfire_1, bonfire_2]
    for i in bonfires:
        temp_state, temp_distance = i.check_entering_in_fire_zone(
            player, optical_flare_borders)  # state entering, distance to player
        temp_entering_in_fire_zones += temp_state
        if temp_state:
            draw_optical_flare = 1
            optical_flare_distance = temp_distance
            temp_flare_x_from = i.x
            temp_flare_y_from = i.y

    # движение игрока
    player.update_position(dt, flat)

    offset_x = -player.x
    offset_y = -player.y

    # тригер начала движения # trigger
    if temp_player_x != player.x or temp_player_y != player.y:
        global text_greeting, step_sound_duration_last_played
        if text_greeting.show:
            if text_greeting.show_text == 1:
                text_greeting.hide()
                text_optical_flares.show()

        if time.time() - step_sound_duration_last_played > step_sound_duration:
            step_sound.play()
            step_sound_duration_last_played = time.time()

    # тригеры зоны огня # trigger
    if temp_entering_in_fire_zones > 0:
        if text_optical_flares.show_text == 1:
            text_optical_flares.hide()
        fire_burning_sound.set_volume(
            round((1 - (optical_flare_distance / optical_flare_borders[1])) / 15, 3))
    elif temp_entering_in_fire_zones == 0:
        fire_burning_sound.set_volume(0)


# draw
def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(
            topleft=topleft).center)
    surf.blit(rotated_image, new_rect.topleft)


def draw():
    global all_objects, player, draw_optical_flare, optical_flare_borders, text_greeting_show

    screen.fill(DARK_BLUE)
    all_objects = pygame.Surface((all_objects_width, all_objects_height))
    all_objects.fill(DARK_BLUE)

    # flat image
    all_objects.blit(flat.flat_image, (0, 0))

    # draw objects
    unsorted_objects = [] + bonfires + [player]
    sorted_objects = []
    while unsorted_objects:
        minimum = unsorted_objects[0]
        for i in unsorted_objects:
            if i.y < minimum.y:
                minimum = i
        sorted_objects.append(minimum)
        unsorted_objects.remove(minimum)

    for i in sorted_objects:
        i.update_animation_state()
        i.draw()

    # draw glow
    for i in bonfires:
        all_objects.blit(i.glow_image,
                         (i.x - (i.glow_image.get_width() // 2),
                          i.y - (i.glow_image.get_height() // 2) + 70))

    # overlay
    all_objects.blit(flat.flat_image_overlay, (0, 0))

    # texts
    texts = [text_greeting, text_optical_flares]
    for i in texts:
        i.draw()

    # all objects to screen
    screen.blit(all_objects, (width // 2 + offset_x, height // 2 + offset_y))

    # optical flares
    if draw_optical_flare == 1:
        temp_coff = 255 / \
            ((optical_flare_borders[1] - optical_flare_borders[0]) // 2)
        temp_distance_from_center = abs(
            (optical_flare_distance - optical_flare_borders[0]) - (
                optical_flare_borders[1] - optical_flare_borders[0]) // 2)
        temp_alpha = (
            255 - round(temp_distance_from_center * temp_coff)) - 127
        rel_x, rel_y = player.x - temp_flare_x_from, player.y - temp_flare_y_from
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        star_image.set_alpha(temp_alpha)
        glow_rounds_image.set_alpha(temp_alpha)
        rainbow_rounds_image.set_alpha(temp_alpha)
        glass_image.set_alpha(temp_alpha)
        blitRotateCenter(screen, star_image, (temp_flare_x_from +
                                              offset_x +
                                              (width //
                                               2) -
                                              (star_image.get_width() //
                                               2), temp_flare_y_from +
                                              offset_y +
                                              (height //
                                                  2) -
                                              (star_image.get_height() //
                                                  2) +
                                              30), angle)
        blitRotateCenter(screen, glow_rounds_image, (offset_x +
                                                     (width //
                                                      2) +
                                                     temp_flare_x_from -
                                                     (glow_rounds_image.get_width() //
                                                      2) +
                                                     (player.x -
                                                         temp_flare_x_from) *
                                                     2, offset_y +
                                                     (height //
                                                         2) +
                                                     temp_flare_y_from -
                                                     (glow_rounds_image.get_height() //
                                                         2) +
                                                     3 +
                                                     (player.y -
                                                         temp_flare_y_from) *
                                                     2), angle)
        blitRotateCenter(screen, rainbow_rounds_image, (offset_x +
                                                        (width //
                                                         2) +
                                                        temp_flare_x_from -
                                                        (rainbow_rounds_image.get_width() //
                                                         2) +
                                                        (player.x -
                                                            temp_flare_x_from) *
                                                        1.5, offset_y +
                                                        (height //
                                                            2) +
                                                        temp_flare_y_from -
                                                        (rainbow_rounds_image.get_height() //
                                                            2) +
                                                        3 +
                                                        (player.y -
                                                            temp_flare_y_from) *
                                                        1.5), angle)
        screen.blit(glass_image, (0, 0))
        draw_optical_flare = 0

    # graph
    if draw_graph == 1:
        temp_get_fps = clock.get_fps()
        if temp_get_fps > 50:
            temp_color = GREEN
        elif temp_get_fps > 30:
            temp_color = YELLOW
        else:
            temp_color = RED
        screen.blit(font_retro_gaming_25.render(
            str(int(clock.get_fps())) + " fps", True, temp_color), (0, 0))

        if dt < 0.5 or dt > 1.5:
            temp_color = RED
        elif dt < 0.7 or dt > 1.3:
            temp_color = YELLOW
        else:
            temp_color = GREEN
        screen.blit(
            font_retro_gaming_25.render(
                "dt = " +
                str(f"{float(time.time() - last_time):.{5}f}") +
                " ms",
                True,
                temp_color),
            (0,
             30))
        screen.blit(
            font_retro_gaming_25.render(
                "dt_multiplier = " +
                str(f"{dt:.{5}f}"),
                True,
                temp_color),
            (0,
             60))


# intro
def intro():
    VIDEO_FPS = 60
    time_from_start = time.time()
    pygame.mixer.music.load('data/sounds/intro.ogg')
    pygame.mixer.music.play()
    pygame.display.flip()

    while True:
        current_frame = str(
            round((time.time() - time_from_start) * VIDEO_FPS))
        while len(current_frame) < 3:
            current_frame = "0" + str(current_frame)

        if int(current_frame) < 206:
            file = "data\\intro\\intro_" + current_frame + ".png"
            frame = pygame.image.load(file).convert()
            frame_rect = frame.get_rect()
            screen.blit(frame, frame_rect)
            pygame.display.flip()
        else:
            break
        clock.tick(VIDEO_FPS * 2)


# game loop
intro()
pygame.mixer.music.load("data/sounds/jimbob - Lets Camp By The Lake.ogg")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)

pygame.display.flip()
while game_running:
    for i in pygame.event.get():
        event(i)
    process_logic()
    draw()
    pygame.display.flip()
    clock.tick(MAX_FPS)
pygame.quit()
sys.exit()
