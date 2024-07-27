import pygame
from collections import deque
from .sprite_sheet_array import PygameImageArray
from .ui import UI

class AnimCreator:
    def __init__(self, pygame_image_array_obj: PygameImageArray, scale=1) -> None:
        self.pygame_image_array_obj = pygame_image_array_obj
        self.tile_size = self.pygame_image_array_obj.tile_size
        self._images_array = self.pygame_image_array_obj._images_array
        self.scale = scale

    def config_creator_display_ui(self):
        self.rows, self.cols = self._images_array.shape
        self.screen_width = ((self.cols + 2) * self.tile_size[0]) * self.scale # two tiles for visualizing the animation in the right
        self.screen_height = self.rows * self.tile_size[1] * self.scale

        self.sidebar_line = [((self.cols * self.tile_size[0]) * self.scale, 0),
                             ((self.cols * self.tile_size[0]) * self.scale, self.screen_height)]
    
    def fun(self):
        print("Hi from fun!")

    def run_pygame_display(self):
        # Initialize Pygame
        pygame.init()
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Anim Creator")
        run_anim = False
        clock = pygame.time.Clock()
        selected_sprites = deque()

        self.ui = UI(screen)

        self.ui.add_button("btn1", (300, 200), (100, 50), "click me!", "<b>Click to Start.</b>")
        self.ui.bind_function("btn1", self.fun)

        running = True
        while running:
            frame_time = clock.tick(60)
            time_delta = min(frame_time/1000.0, 0.1)

            hovered_tile = self.get_hoverd_tile()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and (self._images_array.shape[0] > hovered_tile[0] and self._images_array.shape[1] >  hovered_tile[1]):
                    tile_surface = pygame.transform.scale(self._images_array[(hovered_tile[0], hovered_tile[1])], (self.tile_size[0] * self.scale, self.tile_size[1] * self.scale))
                    selected_sprites.append(tile_surface)
                    # selected_sprites.extend([tile_surface]*5)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        run_anim = True
                        
                    if event.key == pygame.K_s:
                        run_anim = False

                    if event.key == pygame.K_c:
                        selected_sprites.clear()

                self.ui.run(event)


            screen.fill((0, 0, 0))
            pygame.draw.line(screen, (255, 0, 0), self.sidebar_line[0], self.sidebar_line[1], width=2)

            for i in range(self.rows):
                for j in range(self.cols):
                    tile_surface = pygame.transform.scale(self._images_array[(i, j)], (self.tile_size[0] * self.scale, self.tile_size[1] * self.scale))
                    screen.blit(tile_surface, (j * self.tile_size[0] * self.scale, i * self.tile_size[1] * self.scale))
                
                    if (i, j) == hovered_tile:# and (i, j) in self._images:
                        pygame.draw.rect(screen, (255, 0, 0), (j * self.tile_size[0] * self.scale, i * self.tile_size[1] * self.scale, self.tile_size[0] * self.scale, self.tile_size[1] * self.scale), 2)
            

            if selected_sprites and run_anim:
                for sprite_surface in self.infinite_sprite_generator(selected_sprites):
                    screen.blit(sprite_surface, ((self.cols) * self.tile_size[0] * self.scale, self.tile_size[1] * self.scale))
            

            self.ui.ui_manager.update(time_delta)

            # surface.blit(self.background_image, (0, 0))  # draw the background

            self.ui.ui_manager.draw_ui(screen)


            # Update window caption with index of hovered tile
            caption_text = f"Tile index: ({int(hovered_tile[0])}, {int(hovered_tile[1])})"
            pygame.display.set_caption(caption_text)

            pygame.display.flip()
            clock.tick(10)

    def run(self):
        """Display the array of images using Pygame."""
        # config the display ui
        self.config_creator_display_ui()
        self.run_pygame_display()


    def get_hoverd_tile(self) -> tuple[int, int]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_tile = (int(mouse_y // (self.tile_size[1] * self.scale)), int(mouse_x // (self.tile_size[0] * self.scale)))
        return hovered_tile

    def infinite_sprite_generator(self, sprite_list: deque):
        yield sprite_list[0]
        sprite_list.rotate(-1)
