# Import libraries 
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import nanomesh
import pymunk

import pymunk.pygame_util
import pygame
pymunk.pygame_util.positive_y_is_up = True


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
    def __init__(self, body, pos, vertices, density=0.1, hide=True):
        self.body = body#pymunk.Body(1, 100)
        self.body.position = pos

        self.shape = pymunk.Poly(self.body, vertices)
        self.shape.density = 0.1
        self.shape.elasticity = 1

        if not hide:
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


def add_sprite_mesh(sprite_image_path:str, image_size:tuple):
    # Reading the Image
    image = Image.open(sprite_image_path)
    image = image.resize(image_size)
    image_gray = image.convert("LA")
    image_np = np.array(image_gray)

    # Convert to binary image (1 where there is sprite, 0 where there is transparency)
    image_bin = np.zeros((image_np.shape[0], image_np.shape[1]))
    image_bin[image_np[:, :, 1] > 0] = 1
    image_bin = image_bin
    image_bin = np.flipud(image_bin).T
    # Generate mesh from binary image
    plane = nanomesh.Image(image_bin)
    mesh = plane.generate_mesh(opts='q30a50')

    triangle_points = []
    vertices = mesh.triangle_dict["vertices"]
    triangle_attributes = mesh.triangle_dict["triangle_attributes"].squeeze()
    triangles = mesh.triangle_dict["triangles"]
    body = pymunk.Body(1, 100)
    for i, j in zip(triangles, triangle_attributes):
        if j != 1:
            four_points = np.array((vertices[i[0]].tolist(), vertices[i[1]].tolist(), vertices[i[2]].tolist())) #, vertices[i[0]].tolist()
            triangle_points.append(Polygon(body, (100, 200), four_points.tolist()).shape)

    return body, triangle_points

