
import pygame
import numpy as np
import matplotlib.pyplot as plt
import os

os.environ["interpolation"] = "False"


from game_manager.src.sprite_sheet_array import PygameImageArray, AnimArray, FrameManager, SpriteText
from game_manager.src.physics import Physics
from game_manager.src.sound import SoundManager

# from game_manager.src.behaviors import Jump
from game_manager.src.levels import LevelManager
from game_manager.src.collision import move_sprite

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
level_manager = LevelManager(0)

level_manager.add_level_from_tmx_path("maps/resources/level1.tmx", "collision")


# dir = os.path.dirname(__file__)
print(os.getcwd())
# print(dir)
dino = PygameImageArray(sprite_sheet_path='graphics/AMBULANCE_CLEAN_ALLD0000-sheet.png', tile_size=(140, 140), scale=0.5)
# dino.plot_it()
scale = (1, 1)
# right_down = AnimArray(dino[0:2, :]).scale(scale).interpolate_frames(3)

# # plt.imshow(pygame.surfarray.pixels3d(right_down.sprite_array[0]).T)
# # plt.show()
# up_right = AnimArray(np.array(list(dino[5]) + list(dino[6])[:-1])).scale(scale).interpolate_frames(3)
go_up = AnimArray(dino[5, :2]).scale(scale)#.interpolate_frames(3)
# go_right = AnimArray(dino[0, :2]).scale(scale).interpolate_frames(3)
go_left = AnimArray(dino[0, :2]).scale(scale)
# go_fast = AnimArray(dino[0, :]).scale(scale).interpolate_frames(3)
# go_down = AnimArray(dino[1, 4:6]).scale(scale).interpolate_frames(3)
# right_up = AnimArray(np.array(list(dino[5]) + list(dino[6])[:-1])[::-1], scale=scale, reverse_sprite=(False, False))
# interpolated_frames = right_down.interpolate_frames(10)
# right_down.save_to_npy('interpolated_frames.npy')

# right_down.save_surfaces("right_down")
# up_right.save_surfaces("up_right")
# go_right.save_surfaces("go_right")
# # go_left.save_surfaces("go_left")
# go_fast.save_surfaces("go_fast")
# go_down.save_surfaces("go_down")

# right_down.sort_by_center()
# right_down = AnimArray(npy_path='interpolated_frames.npy').scale((1,1))
right_down = AnimArray(directory='movements/right_down').scale((1,1))

# right_down = AnimArray(dino[0:2, :]).scale(scale).interpolate_frames(3)

# plt.imshow(pygame.surfarray.pixels3d(right_down.sprite_array[0]).T)
# plt.show()

up_right = AnimArray(directory='movements/up_right').scale((1,1)) 
# go_up = AnimArray(directory='go_up').scale((1,1))
go_right = AnimArray(directory='movements/go_right').scale((1,1))
# go_left = AnimArray(directory='go_left').scale((1,1))
go_fast = AnimArray(directory='movements/go_fast').scale((1,1))
go_down = AnimArray(directory='movements/go_down').scale((1,1))

sprite_text = SpriteText((5, 10),"KidpixiesRegular-p0Z1.ttf", 20, (255, 255, 255))
sound_manager = SoundManager()
sound_manager.add_sound_from_path("level", "audio/level_music.wav")
all_anims = {"R": go_right,
             "L": go_right.filp_x(),
             "D": go_down,
             "U": go_up,
             "R-D": right_down.scale((1, 1)),
             "D-R": right_down.reverse(),
             "U-R":up_right,
             "R-U": up_right.reverse(),
             "default": go_right}

frame_manager = FrameManager()

frame_manager.create_anims("ambulance", all_anims)
pygame.display.set_caption('Spritesheets')



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

        self.speedx = 2
        self.speedy = 2
        self.physics = physics

    def update(self):
        self.image = self.frame_gen.get_frame()
        self.mask = pygame.mask.from_surface(self.image)
        key = pygame.key.get_pressed()
        if key[pygame.K_DOWN]:
            move_sprite(self, 0, self.speedy, level_manager.get_current_level().collision_layers)
            self.frame_gen.add_anim_state("D")
        if key[pygame.K_RIGHT]:
            move_sprite(self, self.speedx, 0, level_manager.get_current_level().collision_layers)
            self.frame_gen.add_anim_state("R")
        if key[pygame.K_UP]:
            move_sprite(self, 0, -self.speedy, level_manager.get_current_level().collision_layers)
            self.frame_gen.add_anim_state("U")
        
        if key[pygame.K_LEFT]:
            move_sprite(self, -self.speedx, 0, level_manager.get_current_level().collision_layers)
            self.frame_gen.add_anim_state("L")

        vx, vy = self.physics.apply_forces()
        move_sprite(self, vx, vy, level_manager.get_current_level().collision_layers)


physics = Physics(gravity=0.01, wind=0.0)
all_sprites = pygame.sprite.Group()
player = Player()

all_sprites.add(player)

BG = (50, 50, 50)
BLACK = (0, 0, 0, 0)

clock = pygame.time.Clock()

x, y = 0, 0

sound_manager.play_by_name("level")
run = True
while run:
    screen.fill(BG)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # screen.blit(frame_manager.get_frame(), (x, y))

    all_sprites.update()
    level_manager.draw(screen)
    # hits = get_tileHitList(player, game.currentLevel.layers[1])

    all_sprites.draw(screen)
    pygame.display.update()
    clock.tick(60)

pygame.quit()
