import random
from dataclasses import dataclass
from typing import List

import numpy as np

import vehicle


@dataclass
class Highway:
    vehicles: List[vehicle.Vehicle]
    height: float  # world height in same units as vehicle positions

    def update(self, dt: float) -> None:
        """
        Advance all vehicles. When one drives off the bottom of the screen,
        respawn it just above the top (very quickly) in a different lane
        when possible, with fresh high-speed settings.
        """
        half_height = self.height / 2.0

        # unique lane x positions for respawn
        lane_xs = sorted({float(car.position[0]) for car in self.vehicles})

        for v in self.vehicles:
            # normal physics integration
            v.update(np.float32(dt))

            # VERY fast respawn: as soon as car is just below the bottom
            if v.position[1] > half_height + vehicle.VEHICLE_LENGTH * 0.1:
                old_x = float(v.position[0])

                # pick a lane different from previous, if possible
                if lane_xs:
                    other_lanes = [x for x in lane_xs if abs(x - old_x) > 1e-3]
                    if other_lanes:
                        v.position[0] = random.choice(other_lanes)
                    else:
                        v.position[0] = old_x  # only one lane

                # respawn just above the top with tiny random offset
                v.position[1] = (
                    -half_height
                    - vehicle.VEHICLE_LENGTH * 0.2
                    - random.uniform(0.0, vehicle.VEHICLE_LENGTH * 0.2)
                )

                # fresh, fairly high speed and desired speed
                v.velocity = np.float32(
                    random.uniform(
                        vehicle.MAX_VELOCITY * 0.6,  # start fairly fast
                        vehicle.MAX_VELOCITY * 0.95,  # just under max
                    )
                )
                if hasattr(v, "desired_speed"):
                    v.desired_speed = random.uniform(
                        vehicle.MAX_VELOCITY * 0.85,  # wants to cruise high
                        vehicle.MAX_VELOCITY,  # up near max speed
                    )


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

    # -------- LANE LAYOUT: VERY CLOSE LANES IN CENTER --------
    num_lanes = 4
    road_width = half_window_width * 1.5

    # pack lanes into the central 40% of the window → very close together
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

        max_velocity = np.float32(random.uniform(90.0, 110.0))
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
