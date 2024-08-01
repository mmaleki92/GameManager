class Physics:
    def __init__(self, gravity=0.5, wind=0.0, dt=0.05):
        self.gravity = gravity
        self.wind = wind
        self.dt = dt

    def apply_forces(self, player, dt, velocity_x, velocity_y, collision_manager):
        velocity_x = self.wind * dt
        velocity_y = self.gravity * dt
                
        moved = collision_manager.move_sprite(player, 0, velocity_y)
        if not moved:
            collision_manager.move_sprite(player, 0, 3)
