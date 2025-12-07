from dataclasses import dataclass
import numpy as np

MAX_VELOCITY = 27.0
MAX_ACCEL = 2.0
MAX_DECEL = -10.0
VEHICLE_LENGTH = 260.0
VEHICLE_WIDTH = 130.0


@dataclass
class Vehicle:
    vid: int
    # Strength of acceleration along the y-axis.
    acceleration: np.float32
    # Velocity along the y-axis.
    velocity: np.float32
    # [x, y]
    position: np.ndarray
    # each car’s preferred cruising speed
    desired_speed: float = MAX_VELOCITY

    def update(self, dt: np.float32):
        self.acceleration = min(max(self.acceleration, MAX_DECEL), MAX_ACCEL)
        self.velocity += self.acceleration * dt
        self.velocity = min(max(self.velocity, 0.0), MAX_VELOCITY)
        self.position[1] += self.velocity * dt
