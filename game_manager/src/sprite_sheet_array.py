import os
from collections import deque
from copy import copy
from natsort import natsorted
import pygame
import numpy as np
import matplotlib.pyplot as plt

# add the following to your code for the interpolation to work
# os.environ["interpolation"] = "True"
if os.environ.get("interpolation") == "True":
    from game_manager.libs.frame_interpolator.surface_interpolator import Interpolator, interpolate_recursively, load_image
    from game_manager.libs.U2Net import u2net_test


class PygameImageArray:
    def __init__(self, tile_size, sprite_sheet_path, scale=1):
        self._images_array = self.extract_tiles_from_spritesheet(sprite_sheet_path, tile_size)
        self.tile_size = tile_size
        self.scale = scale

    def add_image(self, index, image_surface=None, image_path=None):
        """Add a Pygame image at a specific index."""
        if image_path:
            image_surface = pygame.image.load(image_path).convert_alpha()
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
        
        # pygame.quit()

    def extract_tiles_from_spritesheet(self, spritesheet_path, tile_size):
        # pygame.init()
        print(spritesheet_path)
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
        
        # pygame.quit()

        return np.array(self._images)

class AnimArray:
    def __init__(self, sprite_array=None, npy_path=None, directory=None) -> None:
        self.npy_path = npy_path
        if self.npy_path:
            sprite_array = self.load_from_npy(self.npy_path)

        if directory:
            sprite_array = self.load_surfaces(directory)

        if isinstance(sprite_array, pygame.surface.Surface): # there is just one sprite
            sprite_array = np.array([sprite_array])
        # self.pre_transitions = pre_transitions
        self.pre_transition = None
        # self.reverse_sprite = reverse_sprite
        # self.scale = scale
        self.npy_loaded = False
        self.sprite_array: np.array = sprite_array.flatten()

        # self.transform_array()
        self.gen_sprite = self.generate_sprite()

    def reverse(self):
        anime_copy = copy(self)
        anime_copy.sprite_array = anime_copy.sprite_array[::-1] 
        return anime_copy

    def filp_x(self):
        # anime_copy = copy(self)
        # print(self.scale)
        sprite_array_copy = self.sprite_array.copy()
        for n in range(sprite_array_copy.size):
            sprite_array_copy[n] = pygame.transform.flip(sprite_array_copy[n], True, False) 
        return AnimArray(sprite_array_copy)
    
    def filp_y(self):
        # anime_copy = copy(self)
        sprite_array_copy = self.sprite_array.copy()
        for n in range(sprite_array_copy.size):
            sprite_array_copy[n] = pygame.transform.flip(sprite_array_copy[n], False, True) 
        return AnimArray(sprite_array_copy)

    # def sort_by_center(self):
    #     for sprite in self.sprite_array:
    #         rect = sprite.get_rect()
    #         print(rect.centerx)
    
    def transform_array(self):
        for sprite_idx in range(self.sprite_array.size):
            self.sprite_array[sprite_idx] = self.convert(self.sprite_array[sprite_idx])

    def scale(self, scale):
        for sprite_idx in range(self.sprite_array.size):
            sprite = self.sprite_array[sprite_idx]
            sprite_size = sprite.get_size()
            self.sprite_array[sprite_idx] = pygame.transform.scale(sprite, (sprite_size[0] * scale[0], sprite_size[1] * scale[1]))
        return self

    def generate_sprite(self):
        if len(self.sprite_array) == 0:
            raise Exception("Sprite array shouldn't be empty!")
        while True:
            for pre_tran in self.pre_transition:
                for tran in self.pre_transitions[pre_tran].sprite_array:
                    yield tran
        
            for s in self.sprite_array:
                yield s#self.sprite_array[n % len(self.sprite_array)]

    def load_surfaces(self, directory):
        """Load an array of Pygame surfaces from disk."""
        surface_files = [f for f in natsorted(os.listdir(directory)) if f.endswith('.png')]
        sprite_array = np.array([pygame.image.load(os.path.join(directory, f)).convert_alpha() for f in surface_files])
        return sprite_array

    def save_surfaces(self, directory):
        """Save an array of Pygame surfaces to disk."""
        if not os.path.exists(directory):
            os.makedirs(directory)
        for i, surface in enumerate(self.sprite_array):
            file_path = os.path.join(directory, f"{i}.png")
            pygame.image.save(surface, file_path)
            
    def save_to_npy(self, file_path):
        # Convert each surface in sprite_array to numpy array representation
        np_arrays = [pygame.surfarray.array3d(surface) for surface in self.sprite_array]
        np.save(file_path, np_arrays)

    def load_from_npy(self, file_path):
        np_arrays = np.load(file_path, allow_pickle=True)
        # Convert numpy arrays back to pygame surfaces including alpha channel
        surfaces = np.array([pygame.surfarray.make_surface(arr) for arr in np_arrays])
        return surfaces

    def interpolate_frames(self, times_to_interpolate):
        frames_list = []
        for sprite_idx in range(self.sprite_array.size - 1):
            interpolated_frames = self.interpolate_two_surfaces(self.sprite_array[sprite_idx], self.sprite_array[sprite_idx + 1], times_to_interpolate) 
            frames_list.extend(interpolated_frames)
        
        sprite_array_interpolated = np.array(frames_list)

        return AnimArray(sprite_array_interpolated)

    def interpolate_two_surfaces(self, surface_1, surface_2, times_to_interpolate):


        surface_1 = self.ensure_alpha(surface_1)
        surface_2 = self.ensure_alpha(surface_2)

        image_1 = pygame.surfarray.pixels3d(surface_1)
        image_2 = pygame.surfarray.pixels3d(surface_2)

        input_frames = [load_image(image_1), load_image(image_2)]
        interpolator = Interpolator()
        frames = list(interpolate_recursively(input_frames, times_to_interpolate, interpolator))

        surfaces_list = self.array_to_surface(frames)
        return surfaces_list
    
    def alpha_rgb(self, frame, alpha):

        surface_array = np.zeros((frame.shape[0], frame.shape[1], 4), dtype=np.uint8)
        surface_array[..., :3] = frame

        rgb_surface = pygame.surfarray.make_surface(surface_array[..., :3])
        rgb_surface = rgb_surface.convert_alpha()  # Ensure the surface supports alpha

        sizex, sizey = rgb_surface.get_size()
        for y in range(sizex):
            for x in range(sizey):
                rgb_surface.set_at((x, y), (*surface_array[x, y, :3], alpha[x, y, 0]))

        return rgb_surface

    def array_to_surface(self, frames):
        surfaces_list = []
        for frame in frames:
            # Convert the frame array to a Pygame surface
            frame_surf = pygame.surfarray.make_surface(frame * 255)

            # Ensure alpha channel exists
            frame_surf = self.ensure_alpha(frame_surf)

            size_x, size_y = frame_surf.get_size()
            image_rgba_1 = np.zeros((size_x, size_y, 3), dtype=int)
            image_rgba_1[..., 0:3] = frame*255

            alpha_pred = u2net_test.main(image_rgba_1)
            
            img_surf = self.alpha_rgb(frame*255, alpha_pred)

            surfaces_list.append(img_surf)
        return surfaces_list
    
    def ensure_alpha(self, surface):
        """Ensure the surface has an alpha channel."""
        if surface.get_flags() & pygame.SRCALPHA == 0:
            surface = surface.convert_alpha()
        return surface

    def convert_unique_color_to_alpha(self, surface, unique_color, tolerance=10):
        pixels = pygame.surfarray.pixels3d(surface)
        alpha = pygame.surfarray.pixels_alpha(surface)

        # Define a mask for pixels close to the unique color (magenta)
        mask_color = np.all(np.abs(pixels - unique_color) <= tolerance, axis=-1)

        # Define a mask for pixels not matching any color in the original image
        mask_transparent = np.ones_like(alpha, dtype=bool)
        # if not self.npy_path:
        for orig_surf in self.sprite_array:
            orig_pixels = pygame.surfarray.pixels3d(orig_surf)
            mask_transparent &= np.any(np.abs(pixels - orig_pixels) > tolerance, axis=-1)

        # Combine masks: set alpha to 0 where the color is close to unique color or not present in original image
        alpha[mask_color | mask_transparent] = 0

        return surface


class FrameManager:
    def __init__(self) -> None:
        # self.sprite_name = sprite_name
        # self.all_anims = all_anims
        self.frames_dict = {}

    def create_anims(self, sprite_name, all_anims):
        self.frames_dict[sprite_name] = Frames(all_anims)
    
    def frame_genrator(self, sprite_name):
        return self.frames_dict[sprite_name]


class Frames:
    def __init__(self, all_anims={}) -> None:
        self.queue = []
        self.duration_list = []
        self.not_moving_frames = [] # for when not doing anything
        # self.frames_generator = self.gen_frames()
        self.default_frames = []
        self.all_anims = all_anims
        self.anim_state = deque()
        self.current_state = None
        self.add_anim_state("default")
        self.times_between_frames = []

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

    def add_anim_state(self, state):
        if self.anim_state:
            transition = self.anim_state[-1] + "-" + state
            if transition in self.all_anims:
                self.anim_state.append(transition)
                self.add_animarray(self.all_anims[transition])

        if self.anim_state:
            if state != self.anim_state[-1]:
                anim_array = self.all_anims[state]
                self.anim_state.append(state)
                self.add_animarray(anim_array)
                # self.times_between_frames.append(pygame.time.get_ticks())

        else:
            anim_array = self.all_anims[state]
            self.anim_state.append(state)
            self.add_animarray(anim_array)

        if len(self.queue)>1:
            self.queue.pop(0)
        # print(self.anim_state)

        # Update window caption with index of hovered tile
        if len(self.anim_state) < 7:
            caption_text = f"[Debug]  States: {list(self.anim_state)}"
        else:
            caption_text = f"[Debug]  States: {list(self.anim_state)[-5:]}"

        pygame.display.set_caption(caption_text)

    def get_frame(self):
        current_time = len(self.anim_state)#pygame.time.get_ticks()

        if self.queue:
            frame = self.queue[0]
            if len(self.queue)>1:
                self.queue.pop(0)

            
            sample__till_num = 10
            every_n_frame = 3
            if len(self.queue) > sample__till_num:
                # for i in range(0, 20, 2):
                temp = self.queue[:sample__till_num:every_n_frame] + self.queue[sample__till_num:]
                self.queue = temp

            return self.queue[0]

    def add_animarray(self, anim_array:AnimArray):
        for frame in anim_array.sprite_array:
            self.queue.append(frame)


class SpriteText:
    def __init__(self, sprite, distance_x, distance_y, font_szie=20, text_color=(255, 255, 255)):
        # Set up font and text
        self.font_szie = font_szie
        self.font = pygame.font.Font(None, font_szie)  # Default font and size 36
        self.text = "Hello, Pygame!"
        self.text_color = text_color
        self.rect = sprite.get_rect()

        self.distance_x = distance_x
        self.distance_y = distance_y

    def calculate_position(self, xy, scale):
        self.text_x = self.rect.centerx + self.distance_x  + xy[0] 
        self.text_y = self.rect.centery + self.distance_y  + xy[1] 

    def render_text(self, text, xy, screen, scale, label_color=(0, 0, 0)):
        self.calculate_position(xy, scale)
        self.font = pygame.font.Font(None, int(self.font_szie*scale))  # Default font and size 36

        text_surface = self.font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.text_x, self.text_y)
        # self.distance_x *= scale
        # self.distance_y *= scale
        # Draw rectangle around the text
        pygame.draw.rect(screen, label_color, text_rect.inflate(50*scale, 10*scale))  # Inflate to give some padding
        pygame.draw.rect(screen, self.text_color, text_rect.inflate(50*scale, 10*scale), 1)  # Border of the rectangle

        screen.blit(text_surface, text_rect)