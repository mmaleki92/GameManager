
import pygame
# import spritesheet
import numpy as np

from sprite_sheet_array import PygameImageArray, AnimArray, FrameManager

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600



dino = PygameImageArray(tile_size=(140, 140), sprite_sheet_path='AMBULANCE_CLEAN_ALLD0000-sheet.png', scale=0.5)
dino.plot_it()

scale = (1, 1)
right_down = AnimArray(dino[0:2, :]).scale(scale)
up_right = AnimArray(np.array(list(dino[5]) + list(dino[6])[:-1])).scale(scale) 
go_up = AnimArray(dino[5, :2]).scale(scale)
go_right = AnimArray(dino[0, :2]).scale(scale)
go_left = AnimArray(dino[0, :2]).scale(scale)
go_fast = AnimArray(dino[0, :]).scale(scale)
go_down = AnimArray(dino[1, 4:6]).scale(scale)
# right_up = AnimArray(np.array(list(dino[5]) + list(dino[6])[:-1])[::-1], scale=scale, reverse_sprite=(False, False))

# right_down.sort_by_center()

all_anims = {"R": go_right,
             "L": go_right.filp_x(),
            #  "Fast": go_fast,
             "D": go_down,
             "U": go_up,
             "R-D": right_down,
             "D-R": right_down.reverse(),
             "U-R":up_right,
             "R-U": up_right.reverse(),
             "default": go_right
             }

frame_manager = FrameManager(all_anims)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Spritesheets')


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        
        self.image = frame_manager.get_frame()

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speedx = 20
        self.speedy = 20
    
    def update(self):
        self.image = frame_manager.get_frame()

        key = pygame.key.get_pressed()
        if key[pygame.K_DOWN]:
            self.rect.y += self.speedy
            frame_manager.add_anim_state("D")
        if key[pygame.K_RIGHT]:
            self.rect.x += self.speedx
            frame_manager.add_anim_state("R")
        if key[pygame.K_UP]:
            self.rect.y -= self.speedy 
            frame_manager.add_anim_state("U")
        if key[pygame.K_LEFT]:
            self.rect.x -= self.speedx
            frame_manager.add_anim_state("L")

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

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


    # screen.blit(frame_manager.get_frame(), (x, y))
    all_sprites.update()
    all_sprites.draw(screen)

    pygame.display.update()
    clock.tick(20)

pygame.quit()
