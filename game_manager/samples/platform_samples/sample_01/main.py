
import pygame
import os
os.environ["interpolation"] = "False"
from game_manager.src.sprite_sheet_array import (PygameImageArray, AnimArray,
                                                  FrameManager, SpriteText)
from game_manager.src import (levels, cameras, 
                              sound, physics, 
                              collision, creator, behaviors)
import time
pygame.init()
size_ = pygame.display.get_desktop_sizes()[0]
SCREEN_WIDTH = 800#size_[0]
SCREEN_HEIGHT = 600#size_[1]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

dino = PygameImageArray(sprite_sheet_path='graphics/player.png', sprite_sheet_shape=(5, 4))

scale = (1, 1)
bullet_image = PygameImageArray(sprite_sheet_path='graphics/bullets.png', sprite_sheet_shape=(3, 1))

shot = AnimArray(bullet_image[0, 0])
explode = AnimArray(bullet_image[0, 1:])
go_right = AnimArray(directory="go_right")
go_left = AnimArray(directory="go_left")


all_anims = {
             "R": go_right.scale(scale),
             "L": go_left.scale(scale),
            #  "J": jump,
            # "J-R":jump_right,
            # "J-L": jump_left,
             "default": go_right.scale(scale)
             }


bullet_anim = {
            "explode": explode,
             "shot": shot,
             "default": shot
             }

level_manager = levels.LevelManager(0)

level_manager.add_level_from_tmx_path("levels/level1.tmx", ["collision"])

frame_manager = FrameManager()

frame_manager.create_anims("bullet", bullet_anim)

frame_manager.create_anims("ambulance", all_anims)
pygame.display.set_caption('Spritesheets')
dt = 0.5


class Bullet(pygame.sprite.Sprite):
    def __init__(self, object_name="bullet"):
        pygame.sprite.Sprite.__init__(self)

        # self.one_direction = direction
        # # self.direction = (direction[0] * speed, direction[1] * speed)
        # self.center = center
        # self.frame_manager = frame_manager
        # self.damage = damage
        self.frame_gen = frame_manager.frame_generator(object_name)
        self.image = self.frame_gen.get_frame()
        self.rect = self.image.get_rect()
        self.x, self.y = self.rect.x, self.rect.y
        self.rect.centerx = 450
        self.rect.centery = 100
        self.mask = pygame.mask.from_surface(self.image)

        self.speedx = 0
        self.speedy = 0
        self.dead = False
        self.collided = False

        self.last_time = time.time()
        self.dt = 1

    def update(self):
        self.image = self.frame_gen.get_frame()
        self.mask = pygame.mask.from_surface(self.image)
        # self.dt = time.time() - self.last_time
        # self.dt *= 120
        # self.last_time = time.time()
        gravity.apply_forces(self, deltatime, 0, self.speedy, collision_manager)

        key = pygame.key.get_pressed()
        if key[pygame.K_d]:
            self.speedx = 10
            moved = collision_manager.move_sprite(self, self.speedx, 0)
            if not moved:
                self.frame_gen.add_anim_state("explode")
                self.dead = True
                # self.kill()
            else:
                self.frame_gen.add_anim_state("shot")

        if key[pygame.K_a]:
            self.speedx = -10
            moved = collision_manager.move_sprite(self, self.speedx, 0)
            if not moved:
                self.frame_gen.add_anim_state("explode")
                # self.kill()
                self.dead = True
            else:
                self.frame_gen.add_anim_state("shot")
        # if not moved:
        #     self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, speedx=0, speedy=0):
        pygame.sprite.Sprite.__init__(self)
        self.frame_gen = frame_manager.frame_generator("ambulance")
        # self.frame_gen.attached_text = sprite_text        
        self.image = self.frame_gen.get_frame()
        self.mask = pygame.mask.from_surface(self.image)

        self.jumper = behaviors.Jumping(collision_manager)
        self.rect = self.image.get_rect()
        self.x, self.y = self.rect.x, self.rect.y
        self.dead = False
        self.is_jumping = True
        self.is_falling = True

        self.rect.centerx = 420
        self.rect.centery = 100

        self.speedx = speedx
        self.speedy = speedy
        self.jump_count = 0
        self.standing = True

    def update(self):
        self.image = self.frame_gen.get_frame()
        self.mask = pygame.mask.from_surface(self.image)

        gravity.apply_forces(player, deltatime, 0, self.speedy, collision_manager)

        key = pygame.key.get_pressed()
        if key[pygame.K_RIGHT]:
            self.speedx = int(non_l * 2 * deltatime)
            collision_manager.move_sprite(self, self.speedx, 0)
            self.frame_gen.add_anim_state("R")

        if key[pygame.K_LEFT]:
            self.speedx = int(-non_l * 2 * deltatime)
            collision_manager.move_sprite(self, self.speedx, 0)
            self.frame_gen.add_anim_state("L")
  
        if not self.jumper.is_jumping and key[pygame.K_SPACE]:
            self.jumper.start_jumping(self, max_jump)
            self.frame_gen.add_anim_state("J")
            sound_manager.play_by_name("jump", play_once=True)
    
        self.jumper.jump(self, deltatime)
        self.frame_gen.add_anim_state("stop_at_last_frame")

collision_manager = collision.Collision(level_manager.get_current_level().collision_layers)


camera_group = cameras.CameraGroup(["box_target"], SCREEN_HEIGHT, SCREEN_WIDTH)

player = Player()

bullet = Bullet()
bullets = pygame.sprite.Group()

non_l = player.rect.height * scale[1]
gravity = physics.Physics(non_l*3, dt)
max_jump = int(gravity.gravity * 1.7)
bullets.add(player)
bullets.add(bullet)
camera_group.add(player)
camera_group.add(bullet)

BG = (50, 50, 50)
BLACK = (0, 0, 0, 0)

clock = pygame.time.Clock()

level = level_manager.get_current_level()
run = True

sound_manager = sound.SoundManager()
sound_manager.add_sound_from_path("level0", "audio/level_music.wav")
sound_manager.add_sound_from_path("jump", "audio/effects/jump.wav")

sound_manager.play_by_name("level0")

last_time = pygame.time.get_ticks()

while run:

    screen.fill(BG)
    t = pygame.time.get_ticks()
    deltatime = (t - last_time) / 1000
    last_time = t

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    camera_group.update()
    # bullets.update()
    # player.gravity() # TODO: add gravity to the groups of the sprites

    camera_group.custom_draw(bullets, level, level_manager)

    pygame.display.update()

    # clock.tick(50)
    clock.tick(non_l*2)
    # timedelta = round(timedelta / 1000, 2)
    # for s in bullets:
    #     if s.dead:
    #         s.kill()
pygame.quit()


