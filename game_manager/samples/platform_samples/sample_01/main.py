
import pygame
import os
os.environ["interpolation"] = "False"
from game_manager.src.sprite_sheet_array import (PygameImageArray, AnimArray,
                                                  FrameManager, SpriteText)
from game_manager.src import (levels, cameras, 
                              sound, physics, 
                              collision, creator)

pygame.init()
size_ = pygame.display.get_desktop_sizes()[0]
SCREEN_WIDTH = 800#size_[0]
SCREEN_HEIGHT = 600#size_[1]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

dino = PygameImageArray(sprite_sheet_path='graphics/player.png', sprite_sheet_shape=(5, 4))

# anim_creator = creator.AnimCreator(dino, 1.5)
# anim_creator.run()
scale = (1, 1)

go_right = AnimArray(dino[0, :-1]).scale(scale)
go_left = AnimArray(dino[1, :-1]).scale(scale)
jump = AnimArray(dino[2, 0]).scale(scale)

jump_right = AnimArray(dino[2, :-1]).scale(scale)

jump_left = AnimArray(dino[3, :-1]).scale(scale)

all_anims = {
             "R": go_right,
             "L": go_left,
             "J": jump,
            "J-R":jump_right,
            "J-L": jump_left,
             "default": go_right
             }

level_manager = levels.LevelManager(0)

level_manager.add_level_from_tmx_path("levels/level1.tmx", ["collision"])

frame_manager = FrameManager()

frame_manager.create_anims("ambulance", all_anims)
pygame.display.set_caption('Spritesheets')
dt = 0.5
# sprite_text = SpriteText((5, 10),"KidpixiesRegular-p0Z1.ttf", 20, (255, 255, 255))
# import numpy as np

# def gen_jump(jump_count, t):
#     # for i in range(max_jump):
#     return gravity.gravity * t




class Player(pygame.sprite.Sprite):
    def __init__(self, speedx=0, speedy=0):
        pygame.sprite.Sprite.__init__(self)
        self.frame_gen = frame_manager.frame_generator("ambulance")
        # self.frame_gen.attached_text = sprite_text        
        self.image = self.frame_gen.get_frame()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.x, self.y = self.rect.x, self.rect.y

        self.is_jumping = True
        self.is_falling = True

        self.rect.centerx = 420
        self.rect.centery = 100

        self.speedx = speedx
        self.speedy = speedy
        self.jump_count = 0
        self.jump_state = False
        self.standing = True
        self.gen_jump_ = []
        self.jump_time = 0

    def update(self):

        self.image = self.frame_gen.get_frame()
        self.mask = pygame.mask.from_surface(self.image)
        
        vx, vy = gravity.apply_forces(deltatime, 0, self.speedy)
        moved = collision_manager.move_sprite(self, 0, vy)
        if not moved:
            collision_manager.move_sprite(self, 0, 1)
    
        key = pygame.key.get_pressed()
        if key[pygame.K_RIGHT]:
            self.speedx = int(non_l * 2 * deltatime)
            collision_manager.move_sprite(self, self.speedx, 0)
            self.frame_gen.add_anim_state("R")

        if key[pygame.K_LEFT]:
            self.speedx = int(-non_l * 2 * deltatime)
            collision_manager.move_sprite(self, self.speedx, 0)
            self.frame_gen.add_anim_state("L")
  
        if not self.gen_jump_ and key[pygame.K_SPACE]:
            self.standing = collision_manager.is_sprite_standing(self, tolerance=1)
            if self.standing:
                self.gen_jump_ = True#gen_jump(max_jump)
                self.frame_gen.add_anim_state("J")
                self.jump_count = max_jump

        if self.gen_jump_:
            # y = gen_jump(self.jump_count, self.jump_time)
            
            # self.jump_time += deltatime
            # if not moved:
            #     self.jump_time = 0
            #     self.gen_jump_ = False
            if self.jump_count > 0:
                self.jump_count -= 2
                self.speedy = -self.jump_count * deltatime
                moved = collision_manager.move_sprite(self, 0, self.speedy)
                if not moved:
                    # self.jump_time = 0
                    self.gen_jump_ = False
            else:
                self.gen_jump_ = False 
                self.jump_count = max_jump
            # moved = collision_manager.move_sprite(self, 0, -self.jump_count * deltatime)

            # except StopIteration:
            #     self.gen_jump_ = []
            # if not moved:
            #     self.gen_jump_ = []
        # self.speedx, self.speedy = 0, 0
        self.frame_gen.add_anim_state("stop_at_last_frame")

collision_manager = collision.Collision(level_manager.get_current_level().collision_layers)

sound_manager = sound.SoundManager()
sound_manager.add_sound_from_path("level0", "audio/level_music.wav")

camera_group = cameras.CameraGroup(["box_target"], SCREEN_HEIGHT, SCREEN_WIDTH)

player = Player()
non_l = player.rect.height * scale[1]
gravity = physics.Physics(non_l*3, dt)

camera_group.add(player)

BG = (50, 50, 50)
BLACK = (0, 0, 0, 0)

clock = pygame.time.Clock()

level = level_manager.get_current_level()
run = True
sound_manager.play_by_name("level0")

last_time = pygame.time.get_ticks()
max_jump = int(gravity.gravity * 1.7)

while run:
    screen.fill(BG)
    t = pygame.time.get_ticks()
    deltatime = (t - last_time) / 1000
    last_time = t

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    camera_group.update()
    # player.gravity() # TODO: add gravity to the groups of the sprites

    camera_group.custom_draw(player, level, level_manager)

    pygame.display.update()
    # clock.tick(50)
    clock.tick(non_l*3)
    # timedelta = round(timedelta / 1000, 2)
    
pygame.quit()
