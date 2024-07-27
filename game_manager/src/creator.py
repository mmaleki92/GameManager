import pygame
from collections import deque
from .sprite_sheet_array import PygameImageArray
from pygame_texteditor import TextEditor
from .ui import UI

class AnimCreator:
    def __init__(self, pygame_image_array_obj: PygameImageArray, scale=1, FPS=20) -> None:
        self.FPS = FPS
        self.pygame_image_array_obj = pygame_image_array_obj
        self.tile_size = self.pygame_image_array_obj.tile_size
        self._images_array = self.pygame_image_array_obj._images_array
        self.scale = scale
        self.selected_sprites = deque()
        self.run_anim = False

    def config_creator_display_ui(self):
        self.rows, self.cols = self._images_array.shape
        self.screen_width = ((self.cols + 2) * self.tile_size[0]) * self.scale # two tiles for visualizing the animation in the right
        self.screen_height = (self.rows + 0.5) * self.tile_size[1] * self.scale

        self.sidebar_line = [((self.cols * self.tile_size[0]) * self.scale, 0),
                             ((self.cols * self.tile_size[0]) * self.scale, self.screen_height)]

    def clear_animation(self):
        self.selected_sprites.clear()

    def run_animation(self):
        self.run_anim = True

    def run_pygame_display(self, screen, clock):

        self.ui = UI(screen)

        self.ui.add_button("run_btn", (((self.cols)* self.tile_size[0]) * self.scale, ((self.rows - 0.5) * self.tile_size[1]) * self.scale), (self.tile_size[0] * self.scale, self.tile_size[1] * self.scale), "Run", "<b>Click to Start.</b>")
        self.ui.bind_function("run_btn", self.run_animation)

        self.ui.add_button("clear_btn", (((self.cols + 1)* self.tile_size[0]) * self.scale, ((self.rows - 0.5) * self.tile_size[1]) * self.scale), ((self.tile_size[0])* self.scale, self.tile_size[1] * self.scale), "Clear", "<b>Click to Start.</b>")
        self.ui.bind_function("clear_btn", self.clear_animation)

        running = True
        while running:

            screen.fill((0, 0, 0))

            frame_time = clock.tick(self.FPS)
            time_delta = min(frame_time/1000.0, 0.1)

            hovered_tile = self.get_hoverd_tile()
            events = pygame.event.get()
            # event.button
            # 1 - left click
            # 2 - middle click
            # 3 - right click
            # 4 - scroll up
            # 5 - scroll down
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and (self._images_array.shape[0] > hovered_tile[0] and self._images_array.shape[1] >  hovered_tile[1]):
                    if event.button == 1:
                        tile_surface = pygame.transform.scale(self._images_array[(hovered_tile[0], hovered_tile[1])], (self.tile_size[0] * self.scale, self.tile_size[1] * self.scale))
                        self.selected_sprites.append(tile_surface)
                    elif event.button == 3:
                        if self.selected_sprites:
                            self.selected_sprites.pop()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.run_anim = True

                    if event.key == pygame.K_s:
                        self.run_anim = False

                    if event.key == pygame.K_c:
                        self.selected_sprites.clear()
                    
                    if event.key == pygame.K_DOWN:
                        if self.FPS > 1: 
                            self.FPS -= 1
                    elif event.key == pygame.K_UP:
                        if self.FPS < 150:
                            self.FPS += 1

                self.ui.run(event)

 
            pygame.draw.line(screen, (255, 0, 0), self.sidebar_line[0], self.sidebar_line[1], width=2)
            pygame.draw.rect(screen, (255, 0, 0), ((self.cols + 0.5 - 0.1) * self.tile_size[0] * self.scale,
                                                   0.1 * self.tile_size[1] * self.scale,
                                                   1.2 * self.tile_size[0] * self.scale,
                                                   1.3*self.tile_size[1] * self.scale), 1)

            for i in range(self.rows):
                for j in range(self.cols):
                    tile_surface = pygame.transform.scale(self._images_array[(i, j)], (self.tile_size[0] * self.scale, self.tile_size[1] * self.scale))
                    screen.blit(tile_surface, (j * self.tile_size[0] * self.scale, i * self.tile_size[1] * self.scale))
                
                    if (i, j) == hovered_tile:# and (i, j) in self._images:
                        pygame.draw.rect(screen, (255, 0, 0), (j * self.tile_size[0] * self.scale,
                                                                i * self.tile_size[1] * self.scale,
                                                                self.tile_size[0] * self.scale,
                                                                self.tile_size[1] * self.scale
                                                                ), 2)

            if self.selected_sprites and self.run_anim:
                for sprite_surface in self.infinite_sprite_generator(self.selected_sprites):
                    screen.blit(sprite_surface,
                                ((self.cols + 0.5) * self.tile_size[0] * self.scale,
                                 0.2 * self.tile_size[1] * self.scale))

            self.ui.ui_manager.update(time_delta)

            # surface.blit(self.background_image, (0, 0))  # draw the background
            self.FPS_text = self.FPS_font.render(f'FPS: {self.FPS}', True, (0, 255, 0), (0, 0, 0))

            self.ui.ui_manager.draw_ui(screen)
            screen.blit(self.FPS_text, self.FPS_textRect)
            if hovered_tile[0] < self._images_array.shape[0] and hovered_tile[1] < self._images_array.shape[1]: 
                caption_text = f"Tile index: ({int(hovered_tile[0])}, {int(hovered_tile[1])})"
            else:
                caption_text = "Out of range selection!"
            
            pygame.display.set_caption(caption_text)

            pygame.display.flip()
            clock.tick(self.FPS)

    def run(self):
        pygame.init()
        # config the display ui
        self.config_creator_display_ui()
        green = (0, 255, 0)
 
        self.FPS_font = pygame.font.Font('freesansbold.ttf', 10 * self.scale)
        self.FPS_text = self.FPS_font.render(f'FPS: {self.FPS}', True, green, (0, 0, 0))
        self.FPS_textRect = self.FPS_text.get_rect()
        
        X = ((self.cols + 1)* self.tile_size[0]) * self.scale
        
        Y = ((self.rows - 1) * self.tile_size[1]) * self.scale

        self.FPS_textRect.center = (X , Y)
        

        # Initialize Pygame
        screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Anim Creator")

        clock = pygame.time.Clock()

        # run the display
        self.run_pygame_display(screen, clock)


    def get_hoverd_tile(self) -> tuple[int, int]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_tile = (int(mouse_y // (self.tile_size[1] * self.scale)), int(mouse_x // (self.tile_size[0] * self.scale)))
        return hovered_tile

    def infinite_sprite_generator(self, sprite_list: deque):
        yield sprite_list[0]
        sprite_list.rotate(-1)
