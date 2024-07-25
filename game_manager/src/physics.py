class Physics:
    def __init__(self, gravity=0.5, wind=0.0):
        self.gravity = gravity
        self.wind = wind
        self.velocity_x = 0
        self.velocity_y = 0

    def apply_forces(self):
        self.velocity_y += self.gravity
        self.velocity_x += self.wind
        return self.velocity_x, self.velocity_y    

