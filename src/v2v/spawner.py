
def spawn_vehicles(
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
