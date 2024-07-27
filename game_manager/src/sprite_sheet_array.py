import os
from collections import deque
from copy import copy
from natsort import natsorted
import pygame
import numpy as np
from typing import Tuple
# import matplotlib.pyplot as plt

# add the following to your code for the interpolation to work
# os.environ["interpolation"] = "True"
if os.environ.get("interpolation") == "True":
    from game_manager.libs.frame_interpolator.surface_interpolator import Interpolator, interpolate_recursively, load_image
    from game_manager.libs.U2Net import u2net_test


class PygameImageArray:
    """
    A class to handle an array of Pygame images.

    Parameters
    ----------
    tile_size : tuple
        Size of each tile in the sprite sheet.
    sprite_sheet_path : str
        Path to the sprite sheet image file.
    scale : int, optional
        Scaling factor for displaying the images (default is 1).

    Methods
    -------
    add_image(index, image_surface=None, image_path=None)
        Add a Pygame image at a specific index.
    __getitem__(index)
        Return Pygame image at a specific index.
    extract_tiles_from_spritesheet(spritesheet_path, tile_size)
        Extract tiles from the sprite sheet.
    """
    def __init__(self, sprite_sheet_path, tile_size=None, sprite_sheet_shape=None):
        self._images_array = self.extract_tiles_from_spritesheet(sprite_sheet_path, tile_size, sprite_sheet_shape)


    def get_sprite_size(self, sprite_sheet_shape: tuple, sheet_width: int, sheet_height: int)-> Tuple[int, int]:
        """get each sprite size with the number of sprites in the sheet"""
        self.tile_size = (int(sheet_width / sprite_sheet_shape[0]), int(sheet_height / sprite_sheet_shape[1]))
        return self.tile_size

    def add_image(self, index:tuple, image_surface=None, image_path=None):
        """
        Add a Pygame image at a specific index.

        Parameters
        ----------
        index : tuple
            Index position to add the image.
        image_surface : pygame.Surface, optional
            Pygame surface image to add (default is None).
        image_path : str, optional
            Path to the image file to load (default is None).
        """
        if image_path:
            image_surface = pygame.image.load(image_path).convert_alpha()
            self._images[index[0]][index[1]] = image_surface
        elif image_surface:
            self._images[index[0]][index[1]] = image_surface
    
    def __getitem__(self, index:tuple):
        """
        Return Pygame image if present.

        Parameters
        ----------
        index : tuple
            Index position of the image.

        Returns
        -------
        numpy.ndarray
            Pygame image at the specified index.
        """
        return np.array(self._images)[index]

        # pygame.quit()

    def extract_tiles_from_spritesheet(self, spritesheet_path, tile_size, sprite_sheet_shape):
        """
        Extract tiles from the sprite sheet.

        Parameters
        ----------
        spritesheet_path : str
            Path to the sprite sheet image file.
        tile_size : tuple
            Size of each tile in the sprite sheet.

        Returns
        -------
        numpy.ndarray
            Array of extracted Pygame images.
        """
        print(spritesheet_path)
        # Load the sprite sheet
        sprite_sheet = pygame.image.load(spritesheet_path)
        sheet_width, sheet_height = sprite_sheet.get_size()
        
        if sprite_sheet_shape:
            self.tile_size = self.get_sprite_size(sprite_sheet_shape, sheet_width, sheet_height)
        else:
            self.tile_size = tile_size

        # Calculate the number of tiles in x and y directions
        tiles_x = sheet_width // self.tile_size[0]
        tiles_y = sheet_height // self.tile_size[1]

        shape = (tiles_y, tiles_x)
        self._images = [[0 for i in range(shape[1])] for j in range(shape[0])] #np.zeros(shape)
        # pygame_image_array = PygameImageArray(tile_size, (tiles_y, tiles_x))

        for i in range(tiles_x):
            for j in range(tiles_y):
                rect = pygame.Rect(i * self.tile_size[0], j * self.tile_size[1], self.tile_size[0], self.tile_size[1])
                tile_surface = sprite_sheet.subsurface(rect)
                self.add_image((j, i), image_surface=tile_surface)
        
        # pygame.quit()

        return np.array(self._images)


class AnimArray:
    """
    A class to handle animations consisting of arrays of Pygame surfaces.

    Parameters
    ----------
    sprite_array : numpy.ndarray, optional
        Array of Pygame surfaces (default is None).
    npy_path : str, optional
        Path to a .npy file to load surfaces from (default is None).
    directory : str, optional
        Directory to load surfaces from (default is None).

    Methods
    -------
    reverse()
        Reverse the order of the sprite array.
    filp_x()
        Flip the sprites horizontally.
    filp_y()
        Flip the sprites vertically.
    transform_array()
        Apply transformations to the sprite array.
    scale(scale)
        Scale the sprites.
    generate_sprite()
        Generate sprites from the array.
    load_surfaces(directory)
        Load an array of Pygame surfaces from disk.
    save_surfaces(directory)
        Save an array of Pygame surfaces to disk.
    save_to_npy(file_path)
        Save the sprite array to a .npy file.
    load_from_npy(file_path)
        Load the sprite array from a .npy file.
    interpolate_frames(times_to_interpolate)
        Interpolate frames between existing frames.
    interpolate_two_surfaces(surface_1, surface_2, times_to_interpolate)
        Interpolate frames between two surfaces.
    alpha_rgb(frame, alpha)
        Apply alpha channel to RGB frame.
    array_to_surface(frames)
        Convert an array of frames to Pygame surfaces.
    ensure_alpha(surface)
        Ensure the surface has an alpha channel.
    convert_unique_color_to_alpha(surface, unique_color, tolerance=10)
        Convert a unique color in the surface to alpha.
    """
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
        """
        Reverse the order of the sprite array.

        Returns
        -------
        AnimArray
            New AnimArray with reversed sprite array.
        """
        anime_copy = copy(self)
        anime_copy.sprite_array = anime_copy.sprite_array[::-1] 
        return anime_copy

    def filp_x(self):
        """
        Flip the sprites horizontally.

        Returns
        -------
        AnimArray
            New AnimArray with horizontally flipped sprites.
        """
        # anime_copy = copy(self)
        # print(self.scale)
        sprite_array_copy = self.sprite_array.copy()
        for n in range(sprite_array_copy.size):
            sprite_array_copy[n] = pygame.transform.flip(sprite_array_copy[n], True, False) 
        return AnimArray(sprite_array_copy)
    
    def filp_y(self):
        """
        Flip the sprites vertically.

        Returns
        -------
        AnimArray
            New AnimArray with vertically flipped sprites.
        """
        sprite_array_copy = self.sprite_array.copy()
        for n in range(sprite_array_copy.size):
            sprite_array_copy[n] = pygame.transform.flip(sprite_array_copy[n], False, True) 
        return AnimArray(sprite_array_copy)

    # def sort_by_center(self):
    #     for sprite in self.sprite_array:
    #         rect = sprite.get_rect()
    #         print(rect.centerx)
    
    def transform_array(self):
        """
        Apply transformations to the sprite array.
        """
        for sprite_idx in range(self.sprite_array.size):
            self.sprite_array[sprite_idx] = self.convert(self.sprite_array[sprite_idx])

    def scale(self, scale):
        """
        Scale the sprites.

        Parameters
        ----------
        scale : float
            Scaling factor for the sprites.

        Returns
        -------
        AnimArray
            New AnimArray with scaled sprites.
        """
        for sprite_idx in range(self.sprite_array.size):
            sprite = self.sprite_array[sprite_idx]
            sprite_size = sprite.get_size()
            self.sprite_array[sprite_idx] = pygame.transform.scale(sprite, (sprite_size[0] * scale[0], sprite_size[1] * scale[1]))
        return self

    def generate_sprite(self):
        """
        Generator to yield sprites from the array.

        Yields
        ------
        pygame.surface.Surface
            Pygame surface from the sprite array.
        """
        if len(self.sprite_array) == 0:
            raise Exception("Sprite array shouldn't be empty!")
        while True:
            for pre_tran in self.pre_transition:
                for tran in self.pre_transitions[pre_tran].sprite_array:
                    yield tran
        
            for s in self.sprite_array:
                yield s#self.sprite_array[n % len(self.sprite_array)]

    def load_surfaces(self, directory):
        """
        Load an array of Pygame surfaces from disk.

        Parameters
        ----------
        directory : str
            Directory to load surfaces from.

        Returns
        -------
        numpy.ndarray
            Array of loaded Pygame surfaces.
        """
        surface_files = [f for f in natsorted(os.listdir(directory)) if f.endswith('.png')]
        sprite_array = np.array([pygame.image.load(os.path.join(directory, f)).convert_alpha() for f in surface_files])
        return sprite_array

    def save_surfaces(self, directory):
        """
        Save an array of Pygame surfaces to disk.

        Parameters
        ----------
        directory : str
            Directory to save surfaces to.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
        for i, surface in enumerate(self.sprite_array):
            file_path = os.path.join(directory, f"{i}.png")
            pygame.image.save(surface, file_path)
            
    def save_to_npy(self, file_path):
        """
        Save the sprite array to a .npy file.

        Parameters
        ----------
        file_path : str
            Path to save the .npy file.
        """
        np_arrays = [pygame.surfarray.array3d(surface) for surface in self.sprite_array]
        np.save(file_path, np_arrays)

    def load_from_npy(self, file_path):
        """
        Load the sprite array from a .npy file.

        Parameters
        ----------
        file_path : str
            Path to the .npy file.

        Returns
        -------
        numpy.ndarray
            Loaded sprite array.
        """
        np_arrays = np.load(file_path, allow_pickle=True)
        # Convert numpy arrays back to pygame surfaces including alpha channel
        surfaces = np.array([pygame.surfarray.make_surface(arr) for arr in np_arrays])
        return surfaces

    def interpolate_frames(self, times_to_interpolate):
        """
        Interpolate frames between existing frames.

        Parameters
        ----------
        times_to_interpolate : int
            Number of frames to interpolate between each pair of frames.

        Returns
        -------
        AnimArray
            New AnimArray with interpolated frames.
        """
        frames_list = []
        for sprite_idx in range(self.sprite_array.size - 1):
            interpolated_frames = self.interpolate_two_surfaces(self.sprite_array[sprite_idx], self.sprite_array[sprite_idx + 1], times_to_interpolate) 
            frames_list.extend(interpolated_frames)
        
        sprite_array_interpolated = np.array(frames_list)

        return AnimArray(sprite_array_interpolated)

    def interpolate_two_surfaces(self, surface_1, surface_2, times_to_interpolate):
        """
        Interpolate frames between two surfaces.

        Parameters
        ----------
        surface_1 : pygame.Surface
            First surface for interpolation.
        surface_2 : pygame.Surface
            Second surface for interpolation.
        times_to_interpolate : int
            Number of frames to interpolate between the two surfaces.

        Returns
        -------
        list of pygame.Surface
            List of interpolated frames.
        """

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
        """
        Apply alpha channel to RGB frame.

        Parameters
        ----------
        frame : numpy.ndarray
            RGB frame to which alpha channel is applied.
        alpha : int
            Alpha value to apply.

        Returns
        -------
        numpy.ndarray
            Frame with applied alpha channel.
        """
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
        """
        Convert an array of frames to Pygame surfaces.

        Parameters
        ----------
        frames : numpy.ndarray
            Array of frames.

        Returns
        -------
        list of pygame.Surface
            List of Pygame surfaces.
        """
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
        """
        Ensure the surface has an alpha channel.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to ensure has an alpha channel.

        Returns
        -------
        pygame.Surface
            Surface with alpha channel.
        """

        if surface.get_flags() & pygame.SRCALPHA == 0:
            surface = surface.convert_alpha()
        return surface

    def convert_unique_color_to_alpha(self, surface, unique_color, tolerance=10):
        """
        Convert a unique color in the surface to alpha.

        Parameters
        ----------
        surface : pygame.Surface
            Surface in which to convert the color.
        unique_color : tuple
            RGB value of the color to convert.
        tolerance : int, optional
            Tolerance for color matching (default is 10).

        Returns
        -------
        pygame.Surface
            Surface with converted color to alpha.
        """
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
        

    def create_anims(self, sprite_name, all_anims, attached_text=None):
        self.frames_dict[sprite_name] = Frames(all_anims, attached_text)
    
    def frame_generator(self, sprite_name):
        return self.frames_dict[sprite_name]

    # def attach_text(self, sprite_name):

    #     pass
    #     #TODO: attach text to sprites from here instead of the sprite class itself


class Frames:
    def __init__(self, all_anims={}, attached_text=None) -> None:
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

        self.attached_text = attached_text

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
                self.add_animarray(transition, self.all_anims[transition])

        if self.anim_state:
            if state != self.anim_state[-1]:
                anim_array = self.all_anims[state]
                self.anim_state.append(state)
                self.add_animarray(state, anim_array)
                # self.times_between_frames.append(pygame.time.get_ticks())
        else:
            anim_array = self.all_anims[state]
            self.anim_state.append(state)
            self.add_animarray(state, anim_array)

        if len(self.queue)>1:
            self.queue.pop(0)

        if len(self.anim_state) < 7:
            caption_text = f"[Debug]  States: {list(self.anim_state)}"
        else:
            caption_text = f"[Debug]  States: {list(self.anim_state)[-5:]}"

        pygame.display.set_caption(caption_text)

    def get_frame(self):
        # current_time = len(self.anim_state)#pygame.time.get_ticks()

        if self.queue:
            # frame = self.queue[0]
            if len(self.queue)>1:
                self.queue.pop(0)

            
            sample__till_num = 10
            every_n_frame = 3
            if len(self.queue) > sample__till_num:
                # for i in range(0, 20, 2):
                # queue_array = np.array(self.queue)

                # temp = queue_array[:sample__till_num:every_n_frame, 0].tolist() + queue_array[sample__till_num:, 0].tolist()

                temp = self.queue[:sample__till_num:every_n_frame] + self.queue[sample__till_num:]

                
                self.queue = temp
            
            if self.attached_text:
                combined = self.attach_text_to_sprite(self.queue[0], self.attached_text)
                return combined
            else:
                return self.queue[0]

    def add_animarray(self, state: str, anim_array:AnimArray):
        for frame in anim_array.sprite_array:
            self.queue.append(frame)

    def attach_text_to_sprite(self, surface: pygame.Surface, sprite_text):
        # surface.get_rect()
        hight, width = surface.get_size()
        self.text_label = sprite_text # SpriteText2((5, 5))
        text_surface = self.text_label.render_text()
        combined_surface = combine_surfaces(text_surface, surface)
        return combined_surface

class SpriteText:
    def __init__(self, text_size, font_name, font_szie=20, text_color=(255, 0, 0), label_color=(255, 0, 0), scale=1):
        # Set up font and text
        self.font_szie = font_szie
        self.font_name = font_name

        # self.font = pygame.font.Font(self.font_name, font_szie)  # Default font and size 36
        self.text = "Hello, Pygame!"
        self.text_color = text_color
        self.text_size = text_size
        self.label_color = label_color
        self.scale = scale

    def render_text(self):
        self.font = pygame.font.Font(self.font_name, int(self.font_szie*self.scale))  # Default font and size 36
        # text_surface_with_border = pygame.Surface(self.text_size, pygame.SRCALPHA)
        text_surface = self.font.render(self.text, True, self.text_color)
        
        # pygame.draw.rect(text_surface, self.label_color, text_rect.inflate(50*scale, 10*scale))  # Inflate to give some padding
        # pygame.draw.rect(text_surface, self.text_color, text_rect.inflate(50*scale, 10*scale), 1)  # Border of the rectangle

        # text_surface_with_border.blit(text_surface, (0, 0))
        return text_surface

def combine_surfaces(surface_1: pygame.Surface, surface_2: pygame.Surface):
    surface_1_size = surface_1.get_size()
    surface_2_size = surface_2.get_size()

    combine_surface_width = max(surface_1_size[0], surface_2_size[0])
    combine_surface_hight = surface_1_size[1] + surface_2_size[1]

    surface_1_rect = surface_1.get_rect()

    surface_1_rect.centerx = combine_surface_width / 2

    combined_surface = pygame.Surface((combine_surface_width, combine_surface_hight), pygame.SRCALPHA)
    
    # Blit the first surface at position (0, 0)
    combined_surface.blit(surface_1, surface_1_rect)

    # Blit the second surface below the first
    combined_surface.blit(surface_2, (0, surface_1_size[1]))
    return combined_surface
