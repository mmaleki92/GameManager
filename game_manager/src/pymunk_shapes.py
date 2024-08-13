import pygame
import pymunk

def info(body):
    print(f'm={body.mass:.0f} moment={body.moment:.0f}')
    cg = body.center_of_gravity
    print(cg.x, cg.y)

class Box:
    def __init__(self, space,  p0=(10, 10), p1=(690, 230), d=2):
        x0, y0 = p0
        x1, y1 = p1
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for i in range(4):
            segment = pymunk.Segment(space.static_body, pts[i], pts[(i+1)%4], d)
            segment.elasticity = 1
            segment.friction = 1
            space.add(segment)

class Polygon:
    def __init__(self, body, pos, vertices, density=0.1, draw_shape=False):
        self.body = body#pymunk.Body(1, 100)
        self.body.position = pos

        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.density = 0.1
        self.shape.elasticity = 1

        if draw_shape:
            self.shape.color = 0, 0, 0, 0


class Rectangle:
    def __init__(self, space, pos, size=(80, 50)):
        self.body = pymunk.Body()
        self.body.position = pos

        shape = pymunk.Poly.create_box(self.body, size)
        shape.density = 0.1
        shape.elasticity = 1
        shape.friction = 1
        space.add(self.body, shape)

class App:
    def __init__(self, space):
        pygame.init()
        self.screen = pygame.display.set_mode((700, 240))
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.running = True
        self.space = space
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.image.save(self.screen, 'shape.png')

            self.screen.fill((220, 220, 220))
            self.space.debug_draw(self.draw_options)
            pygame.display.update()
            self.space.step(0.01)

        pygame.quit()


def moving_body():
    path = [(650, 100), (600, 200), (650, 300)]
    path_index = 0
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position = 650, 100
    segment = pymunk.Segment(body, (-25, 0), (25, 0), 5)
    segment.friction = 1.0
    segment.group = 1
    segment.color = pygame.Color("blue")
    return body, path, path_index, segment


def add_segment(space, object_type, point_1, point_2, width, color=None):
    if object_type == "static":
        obj_type = space.static_body
    
    return pymunk.Segment(obj_type, point_1, point_2, width)
