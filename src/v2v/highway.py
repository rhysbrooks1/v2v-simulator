import random
from dataclasses import dataclass
from typing import List

import numpy as np

import vehicle


@dataclass
class Highway:
    vehicles: List[vehicle.Vehicle]
    height: float


def create_highway(
    num_vehicles: int,
    height: float,
    half_window_width: float,
) -> Highway:
    """
    Construct a highway with a fixed number of lanes and vehicles.

    :param num_vehicles: how many vehicles total
    :param height: world/viewport height (same as window_height in main)
    :param half_window_width: window_width / 2 from main.py, used to center lanes
    """
    vehicles: List[vehicle.Vehicle] = []

    num_lanes = 4
    road_width = half_window_width * 1.5

    center_width = road_width * 0.4
    margin = (road_width - center_width) / 2.0
    usable_width = max(center_width, 1.0)

    if num_lanes == 1:
        lane_xs = [0.0]
    else:
        lane_spacing = usable_width / (num_lanes - 1)
        lane_xs = [
            -half_window_width + margin + lane_idx * lane_spacing
            for lane_idx in range(num_lanes)
        ]

    half_height = height / 2.0

    for vid in range(num_vehicles):
        lane_idx = vid % num_lanes
        x_pos = lane_xs[lane_idx]

        # random vertical placement along the road
        y_pos = random.uniform(-half_height, half_height)
        position = np.array([x_pos, y_pos], dtype=np.float32)

        max_velocity = np.float32(random.uniform(140.0, 180.0))
        # start fairly fast, want to cruise near max speed
        init_velocity = random.uniform(
            max_velocity * 0.6,
            max_velocity * 0.95,
        )

        v = vehicle.Vehicle(
            vid=vid,
            acceleration=np.float32(0.0),
            velocity=np.float32(init_velocity),
            max_velocity=max_velocity,
            position=position,
            bsm_phase=random.uniform(0.0, 1.0),
        )
        vehicles.append(v)

    return Highway(vehicles=vehicles, height=height)
