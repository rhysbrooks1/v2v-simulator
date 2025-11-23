from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import math
import random

# ==============================
# Configuration Constants
# ==============================

DT = 0.1  # simulation time step (seconds)
HIGHWAY_SPEED_MPS = 27.0  # ~60 mph in m/s
MAX_ACCEL = 2.0           # m/s^2 (gentle acceleration)
MAX_DECEL = -5.0          # m/s^2 (hard braking)
SAFE_GAP = 10.0           # meters, desired following distance
VEHICLE_LENGTH = 4.5      # meters
TTC_COLLISION_THRESHOLD = 3.0  # seconds, for CWM triggers
ROAD_LENGTH = 1000.0      # meters, simple straight road


# ==============================
# Data Classes
# ==============================

@dataclass
class Vehicle:
    vid: int
    x: float              # position along the road (meters)
    v: float              # speed (m/s)
    a: float = 0.0        # acceleration (m/s^2)
    length: float = VEHICLE_LENGTH
    desired_speed: float = HIGHWAY_SPEED_MPS
    max_accel: float = MAX_ACCEL
    max_decel: float = MAX_DECEL  # negative
    # State flags
    collided: bool = False
    imminent_collision: bool = False
    ttc_to_lead: Optional[float] = None  # Time-To-Collision with the vehicle ahead

    def update_kinematics(self, dt: float) -> None:
        """Update position and speed based on current acceleration."""
        # v_new = v + a * dt
        self.v += self.a * dt
        # Do not allow negative speed
        self.v = max(self.v, 0.0)
        # x_new = x + v * dt
        self.x += self.v * dt

        # Wrap around the road (simple loop for demo)
        if self.x > ROAD_LENGTH:
            self.x -= ROAD_LENGTH

    def choose_acceleration(self, lead_vehicle: Optional["Vehicle"]) -> None:
        """
        Simple car-following logic:
        - Try to reach desired_speed.
        - If following a vehicle, maintain safe gap and brake if needed.
        """
        if lead_vehicle is None:
            # No one ahead: accelerate to desired speed
            if self.v < self.desired_speed:
                self.a = self.max_accel
            else:
                self.a = 0.0
            return

        # Distance to lead car (taking into account wrap-around)
        gap = lead_vehicle.x - self.x - lead_vehicle.length
        if gap < 0:
            gap += ROAD_LENGTH

        relative_speed = self.v - lead_vehicle.v  # positive if we are faster

        # Basic following rule:
        # If too close or closing in fast, brake.
        if gap < SAFE_GAP or (relative_speed > 0 and gap / max(relative_speed, 0.1) < TTC_COLLISION_THRESHOLD):
            # Brake
            self.a = self.max_decel
        else:
            # Try to reach desired speed
            if self.v < self.desired_speed:
                self.a = self.max_accel
            else:
                self.a = 0.0


@dataclass
class CollisionEvent:
    time: float
    v1_id: int
    v2_id: int
    position: float


@dataclass
class TTCEvent:
    time: float
    source_id: int
    target_id: int
    ttc: float


# ==============================
# Simulation Engine
# ==============================

@dataclass
class HighwaySimulation:
    vehicles: List[Vehicle] = field(default_factory=list)
    time: float = 0.0
    collisions: List[CollisionEvent] = field(default_factory=list)
    ttc_events: List[TTCEvent] = field(default_factory=list)

    def step(self) -> None:
        """Advance the simulation by one time step (DT)."""

        # 1. Sort vehicles by position along the road
        self.vehicles.sort(key=lambda v: v.x)

        # 2. Determine accelerations based on car-following logic
        n = len(self.vehicles)
        for i, v in enumerate(self.vehicles):
            lead = self.vehicles[(i + 1) % n] if n > 1 else None
            if lead == v:
                lead = None  # Only one car
            v.choose_acceleration(lead)

        # 3. Update positions and speeds
        for v in self.vehicles:
            v.update_kinematics(DT)

        # 4. Check for collisions and TTC events
        self.detect_collisions_and_ttc()

        # 5. Advance time
        self.time += DT

    def detect_collisions_and_ttc(self) -> None:
        """Detect collisions and compute TTC for potential emergencies."""
        self.vehicles.sort(key=lambda v: v.x)
        n = len(self.vehicles)

        # Reset per-step flags
        for v in self.vehicles:
            v.collided = False
            v.imminent_collision = False
            v.ttc_to_lead = None

        for i, follower in enumerate(self.vehicles):
            if n <= 1:
                break

            lead = self.vehicles[(i + 1) % n]
            if lead == follower:
                continue

            # Distance to lead car, accounting for wrap-around
            gap = lead.x - follower.x - lead.length
            if gap < 0:
                gap += ROAD_LENGTH

            # Check collision (overlap)
            if gap <= 0.0:
                follower.collided = True
                lead.collided = True
                collision_pos = follower.x
                self.collisions.append(
                    CollisionEvent(
                        time=self.time,
                        v1_id=follower.vid,
                        v2_id=lead.vid,
                        position=collision_pos,
                    )
                )
                continue

            # Compute TTC if follower is faster
            relative_speed = follower.v - lead.v  # >0 if follower is catching up
            if relative_speed > 0:
                ttc = gap / relative_speed
                follower.ttc_to_lead = ttc

                # If TTC is below threshold, mark as imminent collision
                if ttc < TTC_COLLISION_THRESHOLD:
                    follower.imminent_collision = True
                    self.ttc_events.append(
                        TTCEvent(
                            time=self.time,
                            source_id=follower.vid,
                            target_id=lead.vid,
                            ttc=ttc,
                        )
                    )


# ==============================
# Initialization Helpers
# ==============================

def create_highway_vehicles(
    num_vehicles: int = 10,
    road_length: float = ROAD_LENGTH,
    base_speed: float = HIGHWAY_SPEED_MPS,
) -> List[Vehicle]:
    """
    Create vehicles spaced along a 1D highway with small random variations
    in speed and starting position.
    """
    vehicles = []
    spacing = road_length / num_vehicles

    for i in range(num_vehicles):
        x0 = i * spacing + random.uniform(-2.0, 2.0)
        v0 = base_speed + random.uniform(-3.0, 3.0)  # +/- ~6 mph variation

        vehicles.append(
            Vehicle(
                vid=i,
                x=x0,
                v=max(v0, 0.0),
                desired_speed=base_speed + random.uniform(-2.0, 2.0),
            )
        )

    return vehicles


# ==============================
# Example: Run the Simulation
# ==============================

if __name__ == "__main__":
    # Create a simulation with 12 vehicles
    sim = HighwaySimulation(vehicles=create_highway_vehicles(12))

    SIM_DURATION = 30.0  # seconds
    num_steps = int(SIM_DURATION / DT)

    for step in range(num_steps):
        sim.step()

        # Simple text output every 1 second
        if step % int(1.0 / DT) == 0:
            print(f"\nTime = {sim.time:5.2f} s")
            for v in sim.vehicles:
                ic = "IC!" if v.imminent_collision else "   "
                print(
                    f"Vehicle {v.vid:2d}: x={v.x:7.2f} m, v={v.v:5.2f} m/s, a={v.a:5.2f} m/s^2, {ic}"
                )

    # Summary
    print("\n=== Simulation Summary ===")
    print(f"Total time simulated: {sim.time:.2f} s")
    print(f"Total collisions detected: {len(sim.collisions)}")
    for c in sim.collisions:
        print(f" - t={c.time:.2f}s: Vehicle {c.v1_id} and {c.v2_id} collided at x={c.position:.2f}m")

    print(f"\nTotal TTC events (imminent collision warnings): {len(sim.ttc_events)}")
    if sim.ttc_events:
        print("Example TTC events:")
        for e in sim.ttc_events[:10]:
            print(
                f" - t={e.time:.2f}s: follower={e.source_id}, lead={e.target_id}, TTC={e.ttc:.2f}s"
            )
