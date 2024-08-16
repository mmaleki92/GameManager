from pymunk.vec2d import Vec2d

# WIDTH, HEIGHT = 690, 400
FPS = 60
dt = 1.0 / FPS
PLAYER_VELOCITY = 100.0 * 2.0
PLAYER_GROUND_ACCEL_TIME = 0.05
PLAYER_GROUND_ACCEL = PLAYER_VELOCITY / PLAYER_GROUND_ACCEL_TIME

PLAYER_AIR_ACCEL_TIME = 0.25
PLAYER_AIR_ACCEL = PLAYER_VELOCITY / PLAYER_AIR_ACCEL_TIME



game_configs = {"WIDTH": 690,
                "HEIGHT": 400,
                "dt": dt,
                "FPS": FPS,
                "PLAYER_VELOCITY": 100.0 * 2.0,
                "PLAYER_GROUND_ACCEL_TIME": 0.05,
                "PLAYER_GROUND_ACCEL":  PLAYER_GROUND_ACCEL,
                "PLAYER_AIR_ACCEL_TIME": 0.25,
                "PLAYER_AIR_ACCEL": PLAYER_AIR_ACCEL,
                "JUMP_HEIGHT": 16.0 * 3,
                "JUMP_BOOST_HEIGHT": 24.0,
                "JUMP_CUTOFF_VELOCITY": 100,
                "FALL_VELOCITY": 250.0,
                "JUMP_LENIENCY": 0.05,
                "HEAD_FRICTION": 0.7,
                "PLATFORM_SPEED": 1,
                "remaining_jumps": 2
                }

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
objects = {"box_walls": box_walls,
           "rounded_segments": rounded_segments,
           "platform_segments": platform_segments}
