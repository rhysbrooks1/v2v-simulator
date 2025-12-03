from dataclasses import dataclass
from vehicle import Vehicle
import vehicle
import numpy as np
import random


def create_highway(num_vehicles, height, width):
    vehicles = []

    lanes = 5.0
    lane_offset = -(float(width) / 2.0) + vehicle.VEHICLE_WIDTH / 2.0
    lane_spacing = float(width) / lanes
    for i in range(num_vehicles):
        lane = random.randint(0, int(lanes) - 1)
        vheight = random.uniform(0, height)
        position = np.array(
            [lane * lane_spacing + lane_offset, vheight], dtype=np.float32
        )
        velocity = random.uniform(vehicle.MAX_VELOCITY / 2.0, vehicle.MAX_VELOCITY)

        vehicles += [
            Vehicle(
                i,
                0.0,
                velocity,
                position,
            )
        ]

    return Highway(vehicles, height)


@dataclass
class Highway:
    vehicles: list[Vehicle]
    height: np.float32

    def update(self, dt):
        half_height = self.height / 2.0
        for v in self.vehicles:
            v.update(dt)
            if v.position[1] > half_height:
                v.position[1] = -half_height
