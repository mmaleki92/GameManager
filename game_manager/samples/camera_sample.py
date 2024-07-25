
import pygame
import numpy as np
import matplotlib.pyplot as plt
import os

os.environ["interpolation"] = "False"


from game_manager.src.sprite_sheet_array import PygameImageArray, AnimArray, FrameManager, SpriteText
from game_manager.src import levels, cameras, sound, physics, collision

pygame.init()
size_ = pygame.display.get_desktop_sizes()[0]
SCREEN_WIDTH = size_[0]
SCREEN_HEIGHT = size_[1]


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

dino = PygameImageArray(tile_size=(140, 140), sprite_sheet_path='graphics/AMBULANCE_CLEAN_ALLD0000-sheet.png', scale=0.5)
dino.plot_it()

scale = (0.5, 0.5)


go_up = AnimArray(dino[5, :2]).scale(scale)#.interpolate_frames(3)
# go_right = AnimArray(dino[0, :2]).scale(scale).interpolate_frames(3)
go_left = AnimArray(dino[0, :2]).scale(scale)
# go_fast = AnimArray(dino[0, :]).scale(scale).interpolate_frames(3)
# go_down = AnimArray(dino[1, 4:6]).scale(scale).interpolate_frames(3)
# right_up = AnimArray(np.array(list(dino[5]) + list(dino[6])[:-1])[::-1], scale=scale, reverse_sprite=(False, False))
# interpolated_frames = right_down.interpolate_frames(10)

# right_down.save_surfaces("right_down")
# up_right.save_surfaces("up_right")
# go_right.save_surfaces("go_right")
# # go_left.save_surfaces("go_left")
# go_fast.save_surfaces("go_fast")
# go_down.save_surfaces("go_down")

# right_down.sort_by_center()
# right_down = AnimArray(npy_path='interpolated_frames.npy').scale((1,1))
right_down = AnimArray(directory='movements/right_down').scale((1,1))


up_right = AnimArray(directory='movements/up_right').scale(scale) 
# go_up = AnimArray(directory='go_up').scale((1,1))
go_right = AnimArray(directory='movements/go_right').scale(scale)
# go_left = AnimArray(directory='go_left').scale((1,1))
go_fast = AnimArray(directory='movements/go_fast').scale(scale)
go_down = AnimArray(directory='movements/go_down').scale(scale)


all_anims = {"R": go_right,
             "L": go_right.filp_x(),
             "D": go_down,
             "U": go_up,
             "R-D": right_down.scale(scale),
             "D-R": right_down.reverse(),
             "U-R":up_right,
             "R-U": up_right.reverse(),
             "default": go_right
             }

level_manager = levels.LevelManager(0)

level_manager.add_level_from_tmx_path("maps/resources/level1.tmx", "collision")

frame_manager = FrameManager()

frame_manager.create_anims("ambulance", all_anims)
pygame.display.set_caption('Spritesheets')

sprite_text = SpriteText((5, 10),"KidpixiesRegular-p0Z1.ttf", 20, (255, 255, 255))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.frame_gen = frame_manager.frame_generator("ambulance")
        # self.frame_gen.attached_text = sprite_text        
        self.image = self.frame_gen.get_frame()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.x, self.y = self.rect.x, self.rect.y

        self.rect.centerx = 420
        self.rect.centery = 120

        self.speedx = 20
        self.speedy = 20

    def update(self):
        self.image = self.frame_gen.get_frame()
        self.mask = pygame.mask.from_surface(self.image)
        key = pygame.key.get_pressed()
        if key[pygame.K_DOWN]:
            collision.move_sprite(self, 0, self.speedy, level_manager.get_current_level().collision_layers)
            self.frame_gen.add_anim_state("D")
        if key[pygame.K_RIGHT]:
            collision.move_sprite(self, self.speedx, 0, level_manager.get_current_level().collision_layers)
            self.frame_gen.add_anim_state("R")
        if key[pygame.K_UP]:
            collision.move_sprite(self, 0, -self.speedy, level_manager.get_current_level().collision_layers)
            self.frame_gen.add_anim_state("U")
        
        if key[pygame.K_LEFT]:
            collision.move_sprite(self, -self.speedx, 0, level_manager.get_current_level().collision_layers)
            self.frame_gen.add_anim_state("L")

sound_manager = sound.SoundManager()
sound_manager.add_sound_from_path("level0", "audio/level_music.wav")

camera_group = cameras.CameraGroup(["box_target"], SCREEN_HEIGHT, SCREEN_WIDTH)

player = Player()

camera_group.add(player)

BG = (50, 50, 50)
BLACK = (0, 0, 0, 0)

clock = pygame.time.Clock()

level = level_manager.get_current_level()
run = True
sound_manager.play_by_name("level0")
while run:
    screen.fill(BG)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEWHEEL:
            camera_group.zoom_scale += event.y * 0.03
    
    camera_group.update()

    camera_group.custom_draw(player, level, level_manager)

    pygame.display.update()
    clock.tick(20)

pygame.quit()
