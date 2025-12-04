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

    # Group vehicles by lane
    lane_groups = [[] for _ in range(int(lanes))]
    for i in range(num_vehicles):
        lane_idx = random.randint(0, int(lanes) - 1)
        lane_groups[lane_idx].append(i)

    SAFE_VEHICLE_HEIGHT = 120.0

    # Place each lane independently
    for lane_idx, vehicle_ids in enumerate(lane_groups):
        count = len(vehicle_ids)
        if count == 0:
            continue

        slot_height = height / count
        wiggle_room = slot_height - SAFE_VEHICLE_HEIGHT
        max_jitter = max(wiggle_room, 0.0) / 2.0

        for j, vid in enumerate(vehicle_ids):
            slot_center = (j * slot_height) + (slot_height / 2.0)
            jitter = random.uniform(-max_jitter, max_jitter)

            y_raw = slot_center + jitter
            y_pos = y_raw - (height / 2.0)

            x_pos = lane_idx * lane_spacing + lane_offset
            position = np.array([x_pos, y_pos], dtype=np.float32)

            velocity = random.uniform(
                vehicle.MAX_VELOCITY / 2.0,
                vehicle.MAX_VELOCITY
            )

            vehicles.append(
                Vehicle(
                    vid,
                    0.0,
                    velocity,
                    position,
                )
            )

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
