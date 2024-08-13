from PIL import Image
import numpy as np
import nanomesh
import pymunk
from game_manager.src.pymunk_shapes import Polygon
import pymunk.pygame_util
import pygame

pymunk.pygame_util.positive_y_is_up = True

def get_binary_image(sprite_image_path, image_size):
    image = Image.open(sprite_image_path)
    image = image.resize(image_size)
    image_gray = image.convert("LA")
    image_np = np.array(image_gray)

    image_bin = np.zeros((image_np.shape[0], image_np.shape[1]))
    image_bin[image_np[:, :, 1] > 0] = 1
    image_bin = image_bin
    image_bin = np.flipud(image_bin).T

    return image_bin

def image_to_body(image_bin, draw_shape):
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
            triangle_points.append(Polygon(body, (100, 200), four_points.tolist(), draw_shape).shape)
    return body, triangle_points

def add_sprite_mesh(sprite_image_path:str, image_size:tuple, draw_shape=False):
    image_bin = get_binary_image(sprite_image_path, image_size)

    body, triangle_points = image_to_body(image_bin, draw_shape)

    return body, triangle_points

