import pygame
import math



class BackGround:
    def __init__(self) -> None:
        # self.ground_surf
        pass

    def from_image(self, file_path):
        file_path = "graphics/ground.png"
        self.ground_surf = pygame.image.load(f"{file_path}").convert_alpha()
        self.ground_rect = self.ground_surf.get_rect(topleft = (0,0))

    def get_surface(self):
        return self.ground_surf

def main():
    pygame.init()

    clock = pygame.time.Clock()
    FPS = 60

    SCREEN_WIDTH = 1500
    SCREEN_HEIGHT = 600

    #create game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Endless Scroll")

    #load image
    bg = pygame.image.load("bg.png").convert()
    bg_width = bg.get_width()
    bg_rect = bg.get_rect()

    #define game variables
    scroll = 0
    tiles = math.ceil(SCREEN_WIDTH  / bg_width) + 1

    #game loop
    run = True
    while run:

      clock.tick(FPS)

      #draw scrolling background
      for i in range(0, tiles):
        screen.blit(bg, (i * bg_width + scroll, 0))
        bg_rect.x = i * bg_width + scroll
        pygame.draw.rect(screen, (255, 0, 0), bg_rect, 1)

      #scroll background
      scroll -= 5

      #reset scroll
      if abs(scroll) > bg_width:
        scroll = 0

      #event handler
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          run = False

      pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()