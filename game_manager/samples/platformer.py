"""Showcase of a very basic 2d platformer

The red girl sprite is taken from Sithjester's RMXP Resources:
http://untamed.wild-refuge.net/rmxpresources.php?characters

.. note:: The code of this example is a bit messy. If you adapt this to your 
    own code you might want to structure it a bit differently.
"""

__docformat__ = "reStructuredText"

import math
import sys
import os.path
import numpy as np
import pygame

import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d
from game_manager.src.image_to_mesh import add_sprite_mesh
from rotate_image import blitRotate
from game_manager.src.pymunk_shapes import moving_body
from game_manager.src import sound
from game_manager.src.sprite_sheet_array import PygameImageArray, AnimArray, FrameManager, SpriteText

def cpfclamp(f, min_, max_):
    """Clamp f between min and max"""
    return min(max(f, min_), max_)


def cpflerpconst(f1, f2, d):
    """Linearly interpolate from f1 to f2 by no more than d."""
    return f1 + cpfclamp(f2 - f1, -d, d)

def flipy(y):
    """Small hack to convert chipmunk physics to pygame coordinates"""
    return -y + 600
def handle_impulse(body, grounding, landed_previous, landing, sound_manager):
    """
    Handle the impulse when the player lands on the ground.
    
    Args:
        body: The player's body object.
        grounding: A dictionary containing information about the player's grounding.
        landed_previous: A boolean indicating whether the player had landed in the previous frame.
        landing: A dictionary containing the landing position and countdown for the landing effect.
        sound_manager: The sound manager object to play sound effects.
    
    Returns:
        A tuple of (landed_previous, landing).
    """
    if abs(grounding["impulse"].y) / body.mass > 200 and not landed_previous:
        sound_manager.play_by_name("impulse", play_once=True)
        landing = {"p": grounding["position"], "n": 5}
        landed_previous = True
    else:
        landed_previous = False

    if landing["n"] > 0:
        landing["n"] -= 1

    return landed_previous, landing
def move_platform_body(body, platform_path, platform_path_index):
    # Move the moving platform
    destination = platform_path[platform_path_index]
    current = Vec2d(*body.position)
    distance = current.get_distance(destination)
    if distance < PLATFORM_SPEED:
        platform_path_index += 1
        platform_path_index = platform_path_index % len(platform_path)
        t = 1
    else:
        t = PLATFORM_SPEED / distance
    new = current.interpolate_to(destination, t)

    body.position = new
    body.velocity = (new - current) / dt

    return platform_path_index
width, height = 690, 400
fps = 60
dt = 1.0 / fps
PLAYER_VELOCITY = 100.0 * 2.0
PLAYER_GROUND_ACCEL_TIME = 0.05
PLAYER_GROUND_ACCEL = PLAYER_VELOCITY / PLAYER_GROUND_ACCEL_TIME

PLAYER_AIR_ACCEL_TIME = 0.25
PLAYER_AIR_ACCEL = PLAYER_VELOCITY / PLAYER_AIR_ACCEL_TIME

JUMP_HEIGHT = 16.0 * 3
JUMP_BOOST_HEIGHT = 24.0
JUMP_CUTOFF_VELOCITY = 100
FALL_VELOCITY = 250.0

JUMP_LENIENCY = 0.05

HEAD_FRICTION = 0.7

PLATFORM_SPEED = 1

girl_sprite = PygameImageArray(sprite_sheet_path='xmasgirl1.png',sprite_sheet_shape=(4, 4))

scale = (1, 1)

go_down = AnimArray(girl_sprite[0, :]).scale(scale)#.interpolate_frames(3)
# go_right = AnimArray(dino[0, :2]).scale(scale).interpolate_frames(3)
go_left = AnimArray(girl_sprite[1, :]).scale(scale)
go_right = AnimArray(girl_sprite[2, :]).scale(scale)
go_up = AnimArray(girl_sprite[3, :]).scale(scale)


all_anims = {"R": go_right,
             "L": go_left,
             "D": go_down,
             "U": go_up,
             "default": go_right
             }
frame_manager = FrameManager()

frame_manager.create_anims("girl", all_anims)
frame_gen = frame_manager.frame_generator("girl")

def blit_info(screen, font, clock):
    # Info and flip screen
    screen.blit(
        font.render("fps: " + str(clock.get_fps()), 1, pygame.Color("white")),
        (0, 0),
    )
    screen.blit(
        font.render(
            "Move with Left/Right, jump with Up, press again to double jump",
            1,
            pygame.Color("darkgrey"),
        ),
        (5, height - 35),
    )
    screen.blit(
        font.render("Press ESC or Q to quit", 1, pygame.Color("darkgrey")),
        (5, height - 20),
    )
def update_grounding(body, grounding):
    """
    Update the grounding information for the player.
    
    Args:
        body: The player's body object.
        grounding: A dictionary containing information about the player's grounding.
    """

    def f(arbiter):
        n = -arbiter.contact_point_set.normal
        if n.y > grounding["normal"].y:
            grounding["normal"] = n
            grounding["penetration"] = -arbiter.contact_point_set.points[0].distance
            grounding["body"] = arbiter.shapes[1].body
            grounding["impulse"] = arbiter.total_impulse
            grounding["position"] = arbiter.contact_point_set.points[0].point_b

    grounding.update({
        "normal": Vec2d.zero(),
        "penetration": Vec2d.zero(),
        "impulse": Vec2d.zero(),
        "position": Vec2d.zero(),
        "body": None,
    })
    
    body.each_arbiter(f)
def helper_lines(screen):
    for y in [50, 100, 150, 200, 250, 300]:
        color = pygame.Color("green")
        pygame.draw.line(screen, color, (10, y), (680, y), 1)

def init_physics(screen):
    ### Physics stuff
    space = pymunk.Space()
    space.gravity = Vec2d(0, -1000)
    pymunk.pygame_util.positive_y_is_up = True
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    return space, draw_options


def add_segments(segments, space):
    static = []
    for segment in segments:
        static.append(pymunk.Segment(space.static_body, segment["p1"], segment["p2"], segment["width"]))
    return static

box_walls = [
{"p1": (10, 50), "p2": (300, 50), "width": 3},
{"p1": (300, 50), "p2": (325, 50), "width": 3},
{"p1": (325, 50), "p2": (350, 50), "width": 3},
{"p1": (350, 50), "p2": (375, 50), "width": 3},
{"p1": (375, 50), "p2": (680, 50), "width": 3},
{"p1": (680, 50), "p2": (680, 370), "width": 3},
{"p1": (680, 370), "p2": (10, 370), "width": 3},
{"p1": (10, 370), "p2": (10, 50), "width": 3},
]


rounded_segments = [
{"p1": (500, 50), "p2": (520, 60), "width": 3},
{"p1": (520, 60), "p2": (540, 80), "width": 3},
{"p1": (540, 80), "p2": (550, 100), "width": 3},
{"p1": (350, 50), "p2": (550, 150), "width": 3},
]

platform_segments = [
{"p1": (170, 50), "p2": (270, 150), "width": 3},
{"p1": (270, 100), "p2": (300, 100), "width": 3},
{"p1": (400, 150), "p2": (450, 150), "width": 3},
{"p1": (400, 200), "p2": (450, 200), "width": 3},
{"p1": (220, 200), "p2": (300, 200), "width": 3},
{"p1": (50, 250), "p2": (200, 250), "width": 3},
{"p1": (10, 370), "p2": (50, 250), "width": 3},
]

def save_screen(screen, filename="platformer.png"):
    pygame.image.save(screen, filename)

sound_manager = sound.SoundManager()
sound_manager.add_sound_from_path("impulse", os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx.wav"))


def main():
    ### PyGame init
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 16)

    img_sprite = pygame.image.load(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "platform_samples/sample_01/images/bird.png")
    )

    image_size = (100, 100) 
    img_sprite = pygame.transform.scale(img_sprite, image_size)

    space, draw_options = init_physics(screen)

    static = add_segments(box_walls, space)

    static[1].color = pygame.Color("red")
    static[2].color = pygame.Color("green")
    static[3].color = pygame.Color("red")

    # rounded shape
    rounded = add_segments(rounded_segments, space) 

    # static platforms
    platforms = add_segments(platform_segments, space) 

    for s in static + platforms + rounded:
        s.friction = 1.0
        s.group = 1
    space.add(*static, *platforms, *rounded)

    sprite_body, tringles = add_sprite_mesh("platform_samples/sample_01/images/bird.png", image_size, False)
    space.add(sprite_body, *tringles)
    sprite_body.position = 100, 100

    platform_body, platform_path, platform_path_index, s = moving_body()

    space.add(platform_body, s)

    # pass through platform
    passthrough = pymunk.Segment(space.static_body, (270, 100), (320, 100), 5)
    passthrough.color = pygame.Color("yellow")
    passthrough.friction = 1.0
    passthrough.collision_type = 2
    passthrough.filter = pymunk.ShapeFilter(categories=0b1000)
    space.add(passthrough)

    def passthrough_handler(arbiter, space, data):
        if arbiter.shapes[0].body.velocity.y < 0:
            return True
        else:
            return False

    space.add_collision_handler(1, 2).begin = passthrough_handler

    # player
    body = pymunk.Body(5, float("inf"))
    body.position = 100, 100

    head = pymunk.Circle(body, 10, (0, 5))
    head2 = pymunk.Circle(body, 10, (0, 13))
    feet = pymunk.Circle(body, 10, (0, -5))
    
    mask = pymunk.ShapeFilter.ALL_MASKS() ^ passthrough.filter.categories
    sf = pymunk.ShapeFilter(mask=mask)
    head.filter = sf
    head2.filter = sf
    feet.collision_type = 1
    feet.ignore_draw = head.ignore_draw = head2.ignore_draw = True

    space.add(body, head, feet, head2)

    remaining_jumps = 2
    landing = {"p": Vec2d.zero(), "n": 0}
    frame_number = 0

    landed_previous = False

    while running:
        grounding = {
            "normal": Vec2d.zero(),
            "penetration": Vec2d.zero(),
            "impulse": Vec2d.zero(),
            "position": Vec2d.zero(),
            "body": None,
        }

        # Update grounding
        update_grounding(body, grounding)

        well_grounded = False
        if (
            grounding["body"] is not None
            and abs(grounding["normal"].x / grounding["normal"].y) < feet.friction
        ):
            well_grounded = True
            remaining_jumps = 2

        ground_velocity = Vec2d.zero()
        if well_grounded:
            ground_velocity = grounding["body"].velocity

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                save_screen(screen, "platformer.png")

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if well_grounded or remaining_jumps > 0:
                    jump_v = math.sqrt(2.0 * JUMP_HEIGHT * abs(space.gravity.y))
                    impulse = (0, body.mass * (ground_velocity.y + jump_v))
                    body.apply_impulse_at_local_point(impulse)
                    remaining_jumps -= 1
            elif event.type == pygame.KEYUP and event.key == pygame.K_UP:
                sprite_body.velocity = body.velocity.x, min(
                    body.velocity.y, JUMP_CUTOFF_VELOCITY
                )
                body.velocity = body.velocity.x, min(
                    body.velocity.y, JUMP_CUTOFF_VELOCITY
                )

        # Target horizontal velocity of player
        target_vx = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            frame_gen.add_anim_state("L")
            target_vx -= PLAYER_VELOCITY
        if keys[pygame.K_RIGHT]:
            frame_gen.add_anim_state("R")
            target_vx += PLAYER_VELOCITY
        if keys[pygame.K_DOWN]:
            frame_gen.add_anim_state("D")

        feet.surface_velocity = -target_vx, 0

        if grounding["body"] is not None:
            feet.friction = -PLAYER_GROUND_ACCEL / space.gravity.y
            head.friction = HEAD_FRICTION
        else:
            feet.friction, head.friction = 0, 0

        # Air control
        if grounding["body"] is None:
            body.velocity = Vec2d(
                cpflerpconst(
                    body.velocity.x,
                    target_vx + ground_velocity.x,
                    PLAYER_AIR_ACCEL * dt,
                ),
                body.velocity.y,
            )

        body.velocity = body.velocity.x, max(
            body.velocity.y, -FALL_VELOCITY
        )  # clamp upwards as well?

        # Handle landing impulse
        landed_previous, landing = handle_impulse(body, grounding, landed_previous, landing, sound_manager)

        # Move the moving platform
        platform_path_index = move_platform_body(platform_body, platform_path, platform_path_index)

        # ### Clear screen
        screen.fill(pygame.Color("black"))

        ### Helper lines
        helper_lines(screen)
        
        space.debug_draw(draw_options)

        position = body.position + (-16, 28)
        p = pymunk.pygame_util.to_pygame(position, screen)

        angle = np.rad2deg(sprite_body.angle)

        screen_height = screen.get_height()

        pos = (sprite_body.position.x, screen_height - sprite_body.position.y)
        blitRotate(screen, img_sprite, pos, (0, image_size[1]), angle)

        img = frame_gen.get_frame()
        mask = pygame.mask.from_surface(img)
        screen.blit(img, p)

        if landing["n"] > 0:
            p = pymunk.pygame_util.to_pygame(landing["p"], screen)
            pygame.draw.circle(screen, pygame.Color("yellow"), p, 5)

        blit_info(screen, font, clock)
        pygame.display.flip()
        frame_number += 1

        ### Update physics

        space.step(dt)

        clock.tick(fps)

if __name__ == "__main__":
    sys.exit(main())
