
import pygame
# import spritesheet
import numpy as np

from sprite_sheet_array import PygameImageArray, AnimArray, FrameManager

pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

dino = PygameImageArray(tile_size=(140, 140), sprite_sheet_path='AMBULANCE_CLEAN_ALLD0000-sheet.png', scale=0.5)
dino.plot_it()
right_down = AnimArray(dino[0:2, :], scale=0.5, reverse=(False, False))

up_right = AnimArray(np.array(list(dino[5]) + list(dino[6])[:-1]), scale=0.5, reverse=(False, False)) 
go_up = AnimArray(dino[5, :2], scale=0.5, reverse=(False, False))
go_right = AnimArray(dino[0, :2], scale=0.5, reverse=(False, False))
go_left = AnimArray(dino[0, :2], scale=0.5, reverse=(True, Tru))
go_fast = AnimArray(dino[0, :], scale=0.5, reverse=(False, False))
go_down = AnimArray(dino[1, 4:6], scale=0.5, reverse=(False, False))
right_up = AnimArray(np.array(list(dino[5]) + list(dino[6])[:-1])[::-1], scale=0.5, reverse=(False, False))

all_anims = {"R": go_right,
			 "L": go_left,
			 "Fast": go_fast,
			 "D": go_down,
			 "U": go_up,
			 "R-D": right_down,
			 "U-R":up_right,
			 "R-U": right_up,
			 "default": go_right}

frame_manager = FrameManager(all_anims)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Spritesheets')

# frame_manager.set_default_anim(go_right)
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

	key = pygame.key.get_pressed()
	# if key[pygame.K_RIGHT]:
	# 	x += 5
	# 	screen.blit(go_right.get_sprtie(), (x, y))
	# if key[pygame.K_t]:
	# 	screen.blit(go_right.get_sprtie(pre_transition=["turn_right_from_right"]), (x, y))

	if key[pygame.K_DOWN]:
		y += 2
		frame_manager.add_anim_state("D")
	if key[pygame.K_RIGHT]:
		x += 2
		frame_manager.add_anim_state("R")
	if key[pygame.K_UP]:
		y -= 2 
		frame_manager.add_anim_state("U")
	if key[pygame.K_LEFT]:
		x -= 2
		frame_manager.add_anim_state("L")
	screen.blit(frame_manager.get_frame(), (x, y))

	pygame.display.update()
	clock.tick(10)

pygame.quit()
