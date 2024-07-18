
import pygame
import numpy as np
import matplotlib.pyplot as plt
from game_manager.src.sprite_sheet_array import PygameImageArray, AnimArray, FrameManager, SpriteText
from game_manager.src.cameras import CameraGroup

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

dino = PygameImageArray(tile_size=(140, 140), sprite_sheet_path='graphics/AMBULANCE_CLEAN_ALLD0000-sheet.png', scale=0.5)
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


all_anims = {"R": go_right,
             "L": go_right.filp_x(),
            #  "Fast": go_fast,
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
        self.frame_gen = frame_manager.frame_genrator("ambulance")
        self.image = self.frame_gen.get_frame()

        self.rect = self.image.get_rect()
        self.text_label = SpriteText(self.image, 0, -self.rect.centery)
        
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speedx = 20
        self.speedy = 20

    def update(self):
        self.image = self.frame_gen.get_frame()

        key = pygame.key.get_pressed()
        if key[pygame.K_DOWN]:
            self.rect.y += self.speedy
            self.frame_gen.add_anim_state("D")
        if key[pygame.K_RIGHT]:
            self.rect.x += self.speedx
            self.frame_gen.add_anim_state("R")
        if key[pygame.K_UP]:
            self.rect.y -= self.speedy 
            self.frame_gen.add_anim_state("U")
        if key[pygame.K_LEFT]:
            self.rect.x -= self.speedx
            self.frame_gen.add_anim_state("L")

camera_group = CameraGroup(["zoom_keyboard_control", "box_target"], SCREEN_HEIGHT, SCREEN_WIDTH)
# all_sprites = pygame.sprite.Group()
player = Player()
player2 = Player()

# all_sprites.add(player)

# all_sprites.add(player2)

camera_group.add(player)

camera_group.add(player2)

BG = (50, 50, 50)
BLACK = (0, 0, 0, 0)

clock = pygame.time.Clock()

x, y = 0, 0

run = True
while run:
    screen.fill(BG)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEWHEEL:
            camera_group.zoom_scale += event.y * 0.03

    # screen.blit(frame_manager.get_frame(), (x, y))
    # all_sprites.update()
    # all_sprites.draw(screen)

    camera_group.update()
    camera_group.custom_draw(player)

    pygame.display.update()
    clock.tick(30)

pygame.quit()
