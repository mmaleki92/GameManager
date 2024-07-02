import pygame
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

class PygameImageArray:
    def __init__(self, tile_size, sprite_sheet_path, scale):
        self._images_array = self.extract_tiles_from_spritesheet(sprite_sheet_path, tile_size)
        self.tile_size = tile_size
        self.scale = scale

    def add_image(self, index, image_surface=None, image_path=None):
        """Add a Pygame image at a specific index."""
        if image_path:
            image_surface = pygame.image.load(image_path)
            self._images[index[0]][index[1]] = image_surface
        elif image_surface:
            self._images[index[0]][index[1]] = image_surface
            
    def __getitem__(self, index):
        """Override __getitem__ to return Pygame image if present."""
        return np.array(self._images)[index]

    def plot_it(self):
        """Display the array of images using Pygame."""
        rows, cols = self._images_array.shape
        screen_width = cols * self.tile_size[0] * self.scale
        screen_height = rows * self.tile_size[1] * self.scale
        # Initialize Pygame
        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Pygame Image Array")

        # Font for displaying text in caption
        font = pygame.font.SysFont('Arial', 16)
        
        running = True
        while running:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            hovered_tile = (mouse_y // (self.tile_size[1] * self.scale), mouse_x // (self.tile_size[0] * self.scale))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((0, 0, 0))

            for i in range(rows):
                for j in range(cols):
                    # if (i, j) in self._images:
                    tile_surface = pygame.transform.scale(self._images_array[(i, j)], (self.tile_size[0] * self.scale, self.tile_size[1] * self.scale))
                    screen.blit(tile_surface, (j * self.tile_size[0] * self.scale, i * self.tile_size[1] * self.scale))
                
                    if (i, j) == hovered_tile:# and (i, j) in self._images:
                        pygame.draw.rect(screen, (255, 0, 0), (j * self.tile_size[0] * self.scale, i * self.tile_size[1] * self.scale, self.tile_size[0] * self.scale, self.tile_size[1] * self.scale), 2)
            
            # Update window caption with index of hovered tile
            caption_text = f"Tile index: ({int(hovered_tile[0])}, {int(hovered_tile[1])})"
            pygame.display.set_caption(caption_text)

            pygame.display.flip()
        
        pygame.quit()

    def extract_tiles_from_spritesheet(self, spritesheet_path, tile_size):
        pygame.init()

        # Load the sprite sheet
        sprite_sheet = pygame.image.load(spritesheet_path)
        sheet_width, sheet_height = sprite_sheet.get_size()

        # Calculate the number of tiles in x and y directions
        tiles_x = sheet_width // tile_size[0]
        tiles_y = sheet_height // tile_size[1]

        shape = (tiles_y, tiles_x)
        self._images = [[0 for i in range(shape[1])] for j in range(shape[0])] #np.zeros(shape)
        # pygame_image_array = PygameImageArray(tile_size, (tiles_y, tiles_x))

        for i in range(tiles_x):
            for j in range(tiles_y):
                rect = pygame.Rect(i * tile_size[0], j * tile_size[1], tile_size[0], tile_size[1])
                tile_surface = sprite_sheet.subsurface(rect)
                self.add_image((j, i), image_surface=tile_surface)
        
        pygame.quit()

        return np.array(self._images)

class AnimArray:
    def __init__(self, sprite_array, scale, reverse=(False, False), pre_transitions={}) -> None:
        if isinstance(sprite_array, pygame.surface.Surface): # there is just one sprite
            sprite_array = np.array([sprite_array])
        self.pre_transitions = pre_transitions
        self.pre_transition = None
        self.reverse = reverse
        self.sprite_array = sprite_array.flatten()
        self.gen_sprite = self.generate_sprite()
        self.scale = scale

    def generate_sprite(self):
        if len(self.sprite_array) == 0:
            raise Exception("Sprite array shouldn't be empty!")
        while True:
            for pre_tran in self.pre_transition:
                for tran in self.pre_transitions[pre_tran].sprite_array:
                    yield tran
        
            for s in self.sprite_array:
                yield s#self.sprite_array[n % len(self.sprite_array)]

    def get_sprtie(self, pre_transition: list[str]=[]):
        self.pre_transition = pre_transition
        sprite = next(self.gen_sprite)
        sprite_size = sprite.get_size()
        sprite = pygame.transform.scale(sprite, (sprite_size[0]*self.scale, sprite_size[1]*self.scale))
        if any(self.reverse):
            sprite = pygame.transform.flip(sprite, filp_x=self.reverse[0], filp_y=self.reverse[1]) 
        return sprite


class FrameManager:
    def __init__(self, all_anims={}) -> None:
        self.queue = deque([])
        self.duration_list = []
        self.not_moving_frames = [] # for when not doing anything
        self.frames_generator = self.gen_frames()
        self.default_frames = []
        self.all_anims = all_anims
        self.anim_state = []
        self.current_state = None
        self.add_anim_state("default")

    def add_frame(self, frame, duration):
        self.queue.append(frame)
        self.duration_list.append(duration)
 
    def set_default_anim(self, animarray: AnimArray):
        for frame in animarray.sprite_array:
            self.not_moving_frames.append(frame)

    def default_generator(self):
        if len(self.queue) == 0:
            while True:
                for frame in self.not_moving_frames:
                    yield frame

    def gen_frames(self):
        for frame in self.queue:
            yield frame
        
    def add_anim_state(self, state):
        if self.anim_state:
            transition = self.anim_state[-1] + "-" + state
            if transition in self.all_anims:
                self.anim_state.append(transition)
                self.add_animarray(self.all_anims[transition])
        anim_array = self.all_anims[state]
        self.anim_state.append(state)
        self.add_animarray(anim_array)

        if len(self.queue)>1:
            self.queue.popleft()
        print(self.anim_state)

    def get_frame(self):
        if self.queue:
            frame = self.queue[0]
            if len(self.queue)>1:
                self.queue.popleft()
            return self.queue[0] #next(self.frames_generator)

    def add_animarray(self, anim_array:AnimArray):
        for frame in anim_array.sprite_array:
            self.queue.append(frame)

        self.frames_generator = self.gen_frames()

