class Physics:
    def __init__(self, gravity=0.5, wind=0.0, dt=0.05):
        self.gravity = gravity
        self.wind = wind
        self.dt = dt

    def apply_forces(self, dt, velocity_x, velocity_y):
        velocity_x = self.wind * dt
        velocity_y = self.gravity * dt
        return velocity_x, velocity_y    
