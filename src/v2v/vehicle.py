import dataclasses
from dataclasses import dataclass
from messages import BSM, CWM
import numpy as np
import math
import random

MAX_ACCEL = 50.0
MAX_DECEL = -30.0
VEHICLE_LENGTH = 260.0
VEHICLE_WIDTH = 130.0


def dist(src, target) -> float:
    dx = float(src[0]) - float(target[0])
    dy = float(src[1]) - float(target[1])
    return math.sqrt(dx * dx + dy * dy)


@dataclass
class Vehicle:
    vid: int
    # Strength of acceleration along the y-axis.
    acceleration: np.float32
    # Velocity along the y-axis.
    velocity: np.float32
    max_velocity: np.float32
    # [x, y]
    position: np.ndarray

    bsm_phase: float = 0.0
    bsms: list[(BSM, float)] = dataclasses.field(default_factory=list)

    cwm_phase: float = 0.0
    cwms: list[(CWM, float)] = dataclasses.field(default_factory=list)

    def should_emit_bsm(self, phase_increment):
        self.bsm_phase += phase_increment
        if self.bsm_phase >= 1.0:
            self.bsm_phase -= 1.0
            return True
        else:
            return False

    def should_emit_cwm(self, phase_increment):
        self.cwm_phase += phase_increment
        if self.cwm_phase >= 1.0:
            self.cwm_phase -= 1.0
            return True
        else:
            return False

    def emit_bsms(self, dt, vehicles):
        range = 200.0

        if not self.should_emit_bsm(10.0 * dt):
            return 0.0

        for v in vehicles:
            if v.vid == self.vid:
                continue
            if v.position[0] != self.position[0]:
                continue
            if dist(self.position, v.position) <= range:
                # 10% packet loss
                if random.uniform(0.0, 1.0) > 0.1:
                    v.bsms.append(
                        (
                            BSM(
                                sender=self.vid,
                                x=self.position[0],
                                y=self.position[1],
                                speed=self.velocity,
                            ),
                            # 30ms of latency
                            -30.0 / 1000.0,
                        )
                    )

        return range

    def emit_cwms(self, dt, vehicles):
        cwm_range = VEHICLE_LENGTH * 1.2

        remove = []
        for i in range(len(self.bsms)):
            msg, lifetime = self.bsms[i]
            if lifetime > 100.0 / 1000.0:
                remove.append(i)
            self.bsms[i] = (msg, lifetime + dt)

        for i in reversed(remove):
            del self.bsms[i]

        if not self.should_emit_cwm(100.0 * dt):
            return 0.0

        emitted = False

        for i, (bsm, lifetime) in enumerate(self.bsms):
            if lifetime < 0.0:
                continue

            if (
                bsm.y < self.position[1]
                and dist(self.position, [bsm.x, bsm.y]) <= cwm_range
            ):
                for v in vehicles:
                    if v.vid == bsm.sender:
                        emitted = True
                        v.cwms.append(
                            (
                                CWM(
                                    sender=self.vid,
                                    ttc=1.0,
                                ),
                                # 30ms of latency
                                -30.0 / 1000.0,
                            )
                        )

        if emitted:
            return cwm_range
        else:
            return 0.0

    def update(self, dt):
        remove = []
        for i in range(len(self.cwms)):
            msg, lifetime = self.cwms[i]
            if lifetime > 100.0 / 1000.0:
                remove.append(i)
            self.cwms[i] = (msg, lifetime + dt)

        for i in reversed(remove):
            del self.cwms[i]

        if len(self.cwms) > 0:
            self.acceleration = MAX_DECEL
        else:
            self.acceleration = MAX_ACCEL

        self.acceleration = min(max(self.acceleration, MAX_DECEL), MAX_ACCEL)
        self.velocity += self.acceleration * dt
        self.velocity = min(max(self.velocity, 0.0), self.max_velocity)
        self.position[1] += self.velocity * dt
