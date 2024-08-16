
import math
import sys
import os.path
import pygame

import pymunk
import pymunk.pygame_util
from pymunk.vec2d import Vec2d
from game_manager.src.image_to_mesh import add_sprite_mesh
from game_manager.src.image_rotate import blitRotate
from game_manager.src.pymunk_shapes import (moving_body, create_passthrough_platform,
                                            add_segments, move_platform_body,
                                            handle_impulse, cpflerpconst, Grounding)
from game_manager.src import sound
from game_manager.src.sprite_sheet_array import PygameImageArray, AnimArray, FrameManager
from game_settings import *

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
        (5, HEIGHT - 35),
    )
    screen.blit(
        font.render("Press ESC or Q to quit", 1, pygame.Color("darkgrey")),
        (5, HEIGHT - 20),
    )


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

def save_screen(screen, filename="platformer.png"):
    pygame.image.save(screen, filename)

def handle_jump(space, event, body, ground_velocity, remaining_jumps, well_grounded):
    if well_grounded or remaining_jumps > 0:
        jump_v = math.sqrt(2.0 * JUMP_HEIGHT * abs(space.gravity.y))
        impulse = (0, body.mass * (ground_velocity.y + jump_v))
        body.apply_impulse_at_local_point(impulse)
        remaining_jumps -= 1

def create_player(space):
    player_dict = {}
    body = pymunk.Body(5, float("inf"))
    body.position = 100, 100

    head = pymunk.Circle(body, 10, (0, 5))
    head2 = pymunk.Circle(body, 10, (0, 13))
    feet = pymunk.Circle(body, 10, (0, -5))
    
    mask = pymunk.ShapeFilter.ALL_MASKS() ^ pymunk.ShapeFilter(categories=0b1000).categories
    sf = pymunk.ShapeFilter(mask=mask)
    head.filter = sf
    head2.filter = sf
    feet.collision_type = 1
    feet.ignore_draw = head.ignore_draw = head2.ignore_draw = True

    space.add(body, head, feet, head2)
    player_dict["body"] = body
    player_dict["feet"] = feet
    player_dict["head"] = head
    return player_dict

pygame.init()

sound_manager = sound.SoundManager()
sound_manager.add_sound_from_path("impulse", os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx.wav"))

def main():
    ### PyGame init
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

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

    # Create the passthrough platform using the separate function
    create_passthrough_platform(space)

    player_dict = create_player(space)

    remaining_jumps = 2
    landing = {"p": Vec2d.zero(), "n": 0}

    landed_previous = False

    grounding = Grounding()

    while running:
        # Update grounding
        grounding.update(player_dict["body"], player_dict["feet"])

        well_grounded = grounding.is_well_grounded(player_dict["feet"].friction)
        if well_grounded:
            remaining_jumps = 2

        ground_velocity = grounding.ground_velocity()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                save_screen(screen, "platformer.png")

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                handle_jump(space, event, player_dict["body"], ground_velocity, remaining_jumps, well_grounded)
            elif event.type == pygame.KEYUP and event.key == pygame.K_UP:
                sprite_body.velocity = player_dict["body"].velocity.x, min(
                    player_dict["body"].velocity.y, JUMP_CUTOFF_VELOCITY
                )
                player_dict["body"].velocity = player_dict["body"].velocity.x, min(
                    player_dict["body"].velocity.y, JUMP_CUTOFF_VELOCITY
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

        player_dict["feet"].surface_velocity = -target_vx, 0

        if grounding.body is not None:
            player_dict["feet"].friction = -PLAYER_GROUND_ACCEL / space.gravity.y
            player_dict["head"].friction = HEAD_FRICTION
        else:
            player_dict["feet"].friction, player_dict["head"].friction = 0, 0

        # Air control
        if grounding.body is None:
            player_dict["body"].velocity = Vec2d(
                cpflerpconst(
                    player_dict["body"].velocity.x,
                    target_vx + ground_velocity.x,
                    PLAYER_AIR_ACCEL * dt,
                ),
                player_dict["body"].velocity.y,
            )

        player_dict["body"].velocity = player_dict["body"].velocity.x, max(
            player_dict["body"].velocity.y, -FALL_VELOCITY
        )  # clamp upwards as well?

        # Handle landing impulse
        landed_previous, landing = handle_impulse(player_dict["body"], grounding, landed_previous, landing, sound_manager)

        # Move the moving platform
        platform_path_index = move_platform_body(platform_body, platform_path, platform_path_index, PLATFORM_SPEED, dt)

        # ### Clear screen
        screen.fill(pygame.Color("black"))

        ### Helper lines
        helper_lines(screen)
        
        space.debug_draw(draw_options)

        blitRotate(screen, sprite_body, img_sprite, (0, image_size[1]))

        img = frame_gen.get_frame()
        
        position = player_dict["body"].position + (-16, 28)
        p = pymunk.pygame_util.to_pygame(position, screen)

        screen.blit(img, p)

        if landing["n"] > 0:
            p = pymunk.pygame_util.to_pygame(landing["p"], screen)
            pygame.draw.circle(screen, pygame.Color("yellow"), p, 5)

        blit_info(screen, font, clock)
        pygame.display.flip()

        ### Update physics
        space.step(dt)

        clock.tick( )

if __name__ == "__main__":
    sys.exit(main())
