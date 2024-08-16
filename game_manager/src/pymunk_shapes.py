import pygame
import pymunk
from pymunk.vec2d import Vec2d

class Grounding:
    def __init__(self):
        self.normal = Vec2d.zero()
        self.penetration = Vec2d.zero()
        self.impulse = Vec2d.zero()
        self.position = Vec2d.zero()
        self.body = None

    def reset(self):
        self.normal = Vec2d.zero()
        self.penetration = Vec2d.zero()
        self.impulse = Vec2d.zero()
        self.position = Vec2d.zero()
        self.body = None

    def update(self, body, feet):
        self.reset()
        update_grounding(body, self)

    def is_well_grounded(self, feet_friction):
        if self.body is not None and abs(self.normal.x / self.normal.y) < feet_friction:
            return True
        return False

    def ground_velocity(self):
        if self.body is not None:
            return self.body.velocity
        return Vec2d.zero()

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


def get_bounding_box(body):
    x_ = []
    y_ = []
    for shape in body.shapes:
        vertices = [body.local_to_world(v) for v in shape.get_vertices()]
        for v in vertices:
            x_.append(v.x)
            y_.append(v.y)

    min_x, min_y = min(x_), min(y_)
    max_x, max_y = max(x_), max(y_)
    return min_x, min_y, max_x, max_y



def create_passthrough_platform(space):
    """Creates a passthrough platform in the given space."""
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



def add_segments(segments, space):
    static = []
    for segment in segments:
        static.append(pymunk.Segment(space.static_body, segment["p1"], segment["p2"], segment["width"]))
    return static

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
    if abs(grounding.impulse.y) / body.mass > 200 and not landed_previous:
        sound_manager.play_by_name("impulse", play_once=True)
        landing = {"p": grounding.position, "n": 5}
        landed_previous = True
    else:
        landed_previous = False

    if landing["n"] > 0:
        landing["n"] -= 1

    return landed_previous, landing

def move_platform_body(body, platform_path, platform_path_index, PLATFORM_SPEED, dt):
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

def update_grounding(body, grounding):
    """
    Update the grounding information for the player.
    
    Args:
        body: The player's body object.
        grounding: An instance of the Grounding class containing information about the player's grounding.
    """

    def f(arbiter):
        n = -arbiter.contact_point_set.normal
        if n.y > grounding.normal.y:
            grounding.normal = n
            grounding.penetration = -arbiter.contact_point_set.points[0].distance
            grounding.body = arbiter.shapes[1].body
            grounding.impulse = arbiter.total_impulse
            grounding.position = arbiter.contact_point_set.points[0].point_b

    grounding.reset()
    body.each_arbiter(f)
