class Jumping:
    def __init__(self, collision_manager) -> None:
        self.is_falling = True
        self.collision_manager = collision_manager
        self.jump_count = 0
        self.standing = True
        self.max_jump = None
        self.is_jumping = False

    def start_jumping(self, player, max_jump):
        self.max_jump = max_jump
        self.standing = self.collision_manager.is_sprite_standing(player, tolerance=1)
        if self.standing:
            self.is_jumping = True

    def jump(self, player, deltatime):
        
        if self.is_jumping:
            if self.jump_count > 0:
                self.jump_count -= 3
                self.speedy = -self.jump_count * deltatime
                moved = self.collision_manager.move_sprite(player, 0, self.speedy)
                if not moved:
                    self.is_jumping = False
            else:
                self.is_jumping = False 
                self.jump_count = self.max_jump
