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
def cpfclamp(f, min_, max_):
    """Clamp f between min and max"""
    return min(max(f, min_), max_)


def cpflerpconst(f1, f2, d):
    """Linearly interpolate from f1 to f2 by no more than d."""
    return f1 + cpfclamp(f2 - f1, -d, d)

def flipy(y):
    """Small hack to convert chipmunk physics to pygame coordinates"""
    return -y + 600


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
def blit_rotate(surf, image, pos, originPos, angle):
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1]- rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)

    rotated_image_rect = rotated_image.get_rect(center=rotated_image.center)
    
def get_bounding_box(body):
    min_x, min_y = float("-inf"), float("inf")
    max_x, max_y = float("inf"), float("-inf")
    x_ = []
    y_ = []
    for shape in body.shapes:
        vertices = [body.local_to_world(v) for v in shape.get_vertices()]
        for v in vertices:
            x_.append(v.x)
            y_.append(v.y)
            # min_x = min(min_x, v.x)
            # min_y = min(min_y, v.y)
            # max_x = max(max_x, v.x)
            # max_y = max(max_y, v.y)
    min_x, min_y = min(x_), min(y_)
    max_x, max_y = max(x_), max(y_)
    return min_x, min_y, max_x, max_y

def rotate_around_center(image, rect, angle):
    new_image = pygame.transform.rotate(image, angle)
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect

# def rotate(point):
#     # First translates the point to have the origin at your sprite's center.
#     origin = yourSpriteCenterPosition;
#     originPoint = (point[0] - origin[0], point[1] - origin[1])
#     # Then we rotate the point using basic trigonometry.
#     rotatedX = originPoint[0] * np.cos(angle) - originPoint[1] * np.sin(angle)
#     rotatedY = originPoint[0] * np.sin(angle) + originPoint[1] * np.cos(angle)

#     # Finally we need to translate the point back to world space.
#     return (rotatedX + origin[0], rotatedY + origin[1])

def main():

    ### PyGame init
    pygame.init()
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()
    running = True
    font = pygame.font.SysFont("Arial", 16)
    sound = pygame.mixer.Sound(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx.wav")
    )
    img = pygame.image.load(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "xmasgirl1.png")
    )

    img_sprite = pygame.image.load(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "platform_samples/sample_01/images/0.png")
    )#.convert_alpha()

    ### Physics stuff
    space = pymunk.Space()
    space.gravity = Vec2d(0, -1000)
    pymunk.pygame_util.positive_y_is_up = True
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # box walls
    static = [
        pymunk.Segment(space.static_body, (10, 50), (300, 50), 3),
        pymunk.Segment(space.static_body, (300, 50), (325, 50), 3),
        pymunk.Segment(space.static_body, (325, 50), (350, 50), 3),
        pymunk.Segment(space.static_body, (350, 50), (375, 50), 3),
        pymunk.Segment(space.static_body, (375, 50), (680, 50), 3),
        pymunk.Segment(space.static_body, (680, 50), (680, 370), 3),
        pymunk.Segment(space.static_body, (680, 370), (10, 370), 3),
        pymunk.Segment(space.static_body, (10, 370), (10, 50), 3),
    ]
    static[1].color = pygame.Color("red")
    static[2].color = pygame.Color("green")
    static[3].color = pygame.Color("red")

    # rounded shape
    rounded = [
        pymunk.Segment(space.static_body, (500, 50), (520, 60), 3),
        pymunk.Segment(space.static_body, (520, 60), (540, 80), 3),
        pymunk.Segment(space.static_body, (540, 80), (550, 100), 3),
        pymunk.Segment(space.static_body, (550, 100), (550, 150), 3),
    ]

    # static platforms
    platforms = [
        pymunk.Segment(space.static_body, (170, 50), (270, 150), 3)
        # , pymunk.Segment(space.static_body, (270, 100), (300, 100), 5)
        ,
        pymunk.Segment(space.static_body, (400, 150), (450, 150), 3),
        pymunk.Segment(space.static_body, (400, 200), (450, 200), 3),
        pymunk.Segment(space.static_body, (220, 200), (300, 200), 3),
        pymunk.Segment(space.static_body, (50, 250), (200, 250), 3),
        pymunk.Segment(space.static_body, (10, 370), (50, 250), 3),
    ]

    for s in static + platforms + rounded:
        s.friction = 1.0
        s.group = 1
    space.add(*static, *platforms, *rounded)

    # Inside your main function where space is created
    sprite_body, tringles = add_sprite_mesh(space, (width, height), sprite_image_path="platform_samples/sample_01/images/0.png")
    space.add(sprite_body, *tringles)
    sprite_body.position = 100, 100

    # moving platform
    platform_path = [(650, 100), (600, 200), (650, 300)]
    platform_path_index = 0
    platform_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    platform_body.position = 650, 100
    s = pymunk.Segment(platform_body, (-25, 0), (25, 0), 5)
    s.friction = 1.0
    s.group = 1
    s.color = pygame.Color("blue")
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
    # Since we use the debug draw we need to hide these circles. To make it
    # easy we just set their color to black.
    # feet.color = 0, 0, 0, 0
    # head.color = 0, 0, 0, 0
    # head2.color = 0, 0, 0, 0
    mask = pymunk.ShapeFilter.ALL_MASKS() ^ passthrough.filter.categories
    sf = pymunk.ShapeFilter(mask=mask)
    head.filter = sf
    head2.filter = sf
    feet.collision_type = 1
    feet.ignore_draw = head.ignore_draw = head2.ignore_draw = True

    space.add(body, head, feet, head2)
    direction = 1
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
        # find out if player is standing on ground

        def f(arbiter):
            n = -arbiter.contact_point_set.normal
            if n.y > grounding["normal"].y:
                grounding["normal"] = n
                grounding["penetration"] = -arbiter.contact_point_set.points[0].distance
                grounding["body"] = arbiter.shapes[1].body
                grounding["impulse"] = arbiter.total_impulse
                grounding["position"] = arbiter.contact_point_set.points[0].point_b

        body.each_arbiter(f)

        well_grounded = False
        if (
            grounding["body"] != None
            and abs(grounding["normal"].x / grounding["normal"].y) < feet.friction
        ):
            well_grounded = True
            remaining_jumps = 2

        ground_velocity = Vec2d.zero()
        if well_grounded:
            ground_velocity = grounding["body"].velocity

        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and (event.key in [pygame.K_ESCAPE, pygame.K_q])
            ):
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                pygame.image.save(screen, "platformer.png")

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

        if body.velocity.x > 0.01:
            direction = 1
        elif body.velocity.x < -0.01:
            direction = -1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            direction = -1
            target_vx -= PLAYER_VELOCITY
        if keys[pygame.K_RIGHT]:
            direction = 1
            target_vx += PLAYER_VELOCITY
        if keys[pygame.K_DOWN]:
            direction = -3

        feet.surface_velocity = -target_vx, 0

        if grounding["body"] != None:
            feet.friction = -PLAYER_GROUND_ACCEL / space.gravity.y
            head.friction = HEAD_FRICTION
        else:
            feet.friction, head.friction = 0, 0

        # Air control
        if grounding["body"] == None:
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

        # Move the moving platform
        destination = platform_path[platform_path_index]
        current = Vec2d(*platform_body.position)
        distance = current.get_distance(destination)
        if distance < PLATFORM_SPEED:
            platform_path_index += 1
            platform_path_index = platform_path_index % len(platform_path)
            t = 1
        else:
            t = PLATFORM_SPEED / distance
        new = current.interpolate_to(destination, t)
        platform_body.position = new
        platform_body.velocity = (new - current) / dt

        ### Clear screen
        screen.fill(pygame.Color("black"))

        ### Helper lines
        for y in [50, 100, 150, 200, 250, 300]:
            color = pygame.Color("green")
            pygame.draw.line(screen, color, (10, y), (680, y), 1)

        ### Draw stuff
        space.debug_draw(draw_options)
        direction_offset = 48 + (1 * direction + 1) // 2 * 48
        if grounding["body"] != None and abs(target_vx) > 1:
            animation_offset = 32 * (frame_number // 8 % 4)
        elif grounding["body"] is None:
            animation_offset = 32 * 1
        else:
            animation_offset = 32 * 0
        position = body.position + (-16, 28)
        p = pymunk.pygame_util.to_pygame(position, screen)

        # position2 = sprite_body.position + (0, 50)
        # p2 = pymunk.pygame_util.to_pygame(position2, screen)
        # img_sprite = pygame.transform.scale(img_sprite, (40,20))
        # print()
        # img_sprite = pygame.transform.rotate(img_sprite, np.rad2deg(sprite_body.angle)) 
        p2 = sprite_body.position
        p2 = Vec2d(p2.x, -p2.y+screen.get_size()[1] - 50)
   
        # angle_degrees = math.degrees(sprite_body.angle)# + 180
        # rotated_logo_img = pygame.transform.rotate(img_sprite, angle_degrees)


        # offset = Vec2d(*rotated_logo_img.get_size()) / 2
        # p2 = p2 #- offset
        # img_sprite_rect = img_sprite.get_rect()
        # img_sprite_rect.centerx = 
        # img_sprite_rect.centery = 
        # sprite_body.pos
        screen_height = screen.get_height()
        
        min_x, min_y, max_x, max_y = get_bounding_box(sprite_body)
        # max_y = screen_height - max_y
        # min_y = min_y - screen_height 
        # print(min_x, min_y, max_x, max_y)
        width_s = max_x - min_x
        height_s = max_y - min_y
        bounding_rect = pygame.Rect(min_x, screen_height - min_y - height_s, width_s, height_s)

        # screen.blit(rotated_logo_img, (round(p2.x), round(p2.y)))
        # bounding_rect.centerx = width_s / 2
        # bounding_rect.centery = height_s / 2
        # img_sprite.get_rect().center = bounding_rect.center
        pygame.draw.rect(screen, (255, 0, 0), bounding_rect, 3)
        angle = np.rad2deg(sprite_body.angle)

        # img_sprite = pygame.transform.scale(img_sprite, (int(width_s), int(height_s)))
        # img_sprite = pygame.transform.rotate(img_sprite, math.degrees(sprite_body.angle))
        # if abs(int(math.degrees(sprite_body.angle))) > 10:
            # angle = int(math.degrees(sprite_body.angle)) 
        # else:
        #     angle = 0
        # img_sprite, rect = rotate_around_center(img_sprite, img_sprite.get_rect(), angle)
        # pos = (int(min_x), int(screen_height - min_y - height_s-2))
        # pos = (int(min_x), int(screen_height - min_y - height_s-2))
        
        pos = (sprite_body.position.x, screen_height - sprite_body.position.y)
        print(angle)
        blitRotate(screen, img_sprite, pos, (0, 48), angle)
        # print((int(min_x), int(screen_height - min_y - height_s-2)))
        # screen.blit(img_sprite, (int(min_x), int(screen_height - min_y - height_s-2)))

        screen.blit(img, p, (animation_offset, direction_offset, 32, 48))

        # Did we land?
        if abs(grounding["impulse"].y) / body.mass > 200 and not landed_previous:
            sound.play()
            landing = {"p": grounding["position"], "n": 5}
            landed_previous = True
        else:
            landed_previous = False
        if landing["n"] > 0:
            p = pymunk.pygame_util.to_pygame(landing["p"], screen)
            pygame.draw.circle(screen, pygame.Color("yellow"), p, 5)
            landing["n"] -= 1

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

        pygame.display.flip()
        frame_number += 1

        ### Update physics

        space.step(dt)

        clock.tick(fps)


if __name__ == "__main__":
    sys.exit(main())
