import pygame
import time



class Bullet(pygame.sprite.Sprite):
    def __init__(self, direction, center, speed, damage,  frame_manager, object_name):
        self.one_direction = direction
        self.direction = (direction[0] * speed, direction[1] * speed)
        self.center = center
        # self.frame_manager = frame_manager
        self.damage = damage
        self.frame_gen = frame_manager.frame_generator(object_name)
        self.mask = pygame.mask.from_surface(self.image)

        self.image = self.frame_gen.get_frame()

        self.dead = False
        self.collided = False

        self.last_time = time.time()
        self.dt = 1


    def update(self):
        self.image = self.frame_gen.get_frame()
        self.mask = pygame.mask.from_surface(self.image)

        self.dt = time.time() - self.last_time
        self.dt *= 120
        self.last_time = time.time()

# objects should have dead as boolean and fading_time as 
class Fading:
    def __init__(self) -> None:
        self.deads = []

    def check_deads(self):
        end_time = time.time()
        for obj, t in self.deads:
            if end_time - t > obj.fading_time:
                obj.kill()

    def start_counting(self, objects_group):
        for obj in objects_group:
            assert hasattr(obj, "dead")
            assert hasattr(obj, "fading_time")

            if obj.dead and (obj not in self.deads):
                start_time = time.time()
                self.deads.append([obj, start_time])

    def group_fade(self, objects_group):
        self.start_counting(objects_group)

        self.check_deads()