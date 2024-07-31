class Jumping:
    def __init__(self) -> None:
        self.is_jumping = False
        self.is_falling = True

        self.jump_count = 0
        self.standing = True

    def init_jump(self, jump_count, max_jump):
        self.jump_count = jump_count
        self.is_jumping = True
        self.max_jump = max_jump

    def jump(self, deltatime, collision_manager):
        
        if self.is_jumping:
            if self.jump_count > 0:
                self.jump_count -= 3
                self.speedy = -self.jump_count * deltatime
                moved = collision_manager.move_sprite(self, 0, self.speedy)
                if not moved:
                    self.is_jumping = False
            else:
                self.is_jumping = False 
                self.jump_count = self.max_jump
