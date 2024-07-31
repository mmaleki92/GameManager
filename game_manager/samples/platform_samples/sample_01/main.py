
import pygame
import os
os.environ["interpolation"] = "False"
from game_manager.src.sprite_sheet_array import (PygameImageArray, AnimArray,
                                                  FrameManager, SpriteText)
from game_manager.src import (levels, cameras, 
                              sound, physics, 
                              collision, creator, behaviors)

pygame.init()
size_ = pygame.display.get_desktop_sizes()[0]
SCREEN_WIDTH = 800#size_[0]
SCREEN_HEIGHT = 600#size_[1]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

dino = PygameImageArray(sprite_sheet_path='graphics/player.png', sprite_sheet_shape=(5, 4))

scale = (1, 1)


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

level_manager = levels.LevelManager(0)

level_manager.add_level_from_tmx_path("levels/level1.tmx", ["collision"])

frame_manager = FrameManager()

frame_manager.create_anims("ambulance", all_anims)
pygame.display.set_caption('Spritesheets')
dt = 0.5


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

non_l = player.rect.height * scale[1]
gravity = physics.Physics(non_l*3, dt)
max_jump = int(gravity.gravity * 1.7)

camera_group.add(player)

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
    # player.gravity() # TODO: add gravity to the groups of the sprites

    camera_group.custom_draw(player, level, level_manager)

    pygame.display.update()
    # clock.tick(50)
    clock.tick(non_l*3)
    # timedelta = round(timedelta / 1000, 2)
    
pygame.quit()
