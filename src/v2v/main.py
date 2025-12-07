import math
from typing import List, Dict

import numpy as np
import pygame as pg
import OpenGL.GL as gl

import highway
import vehicle
from messages import CWM, BSM
from sprite import SpriteRenderer, load_sprite
from emitter import EmitterRenderer
from line import LineRenderer
from ui_statistics import draw_stats_panel


def dist(src, target) -> float:
    dx = float(src[0]) - float(target[0])
    dy = float(src[1]) - float(target[1])
    return math.sqrt(dx * dx + dy * dy)


def main() -> None:
    bsm_count = 0
    cwm_count = 0
    packet_loss = 1.5
    avg_latency = 8.0
    sim_time = 0.0

    SAFE_DIST = vehicle.VEHICLE_LENGTH * 0.6
    TTC_THRESHOLD = 3.0

    event_timer = 0.0
    EVENT_INTERVAL = 5.0

    message_freq = 1.0 / 10.0
    freq_accumulator = 0.0

    window_width = 1280
    window_height = 720

    pg.init()
    clock = pg.time.Clock()
    running = True

    road = highway.create_highway(
        num_vehicles=12,
        height=window_height,
        half_window_width=window_width / 2.0,
    )

    pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
    pg.display.gl_set_attribute(
        pg.GL_CONTEXT_PROFILE_MASK,
        pg.GL_CONTEXT_PROFILE_CORE,
    )
    pg.display.set_mode(
        (window_width, window_height),
        pg.DOUBLEBUF | pg.OPENGL,
    )

    line_renderer = LineRenderer(window_width, window_height)
    sprite_renderer = SpriteRenderer(window_width, window_height)
    emitter_renderer = EmitterRenderer(window_width, window_height)
    sprite, car_w, car_h = load_sprite("cars/manual.png")

    while running:
        dt = float(clock.tick(60)) / 1_000.0
        sim_time += dt

        event_timer += dt
        if event_timer > EVENT_INTERVAL:
            event_timer = 0.0

            # group cars by lane 
            lanes_for_event: Dict[float, List[vehicle.Vehicle]] = {}
            for car in road.vehicles:
                lane_x = float(car.position[0])
                lanes_for_event.setdefault(lane_x, []).append(car)

            # try to slow one leader in some lane
            for lane_x, cars in lanes_for_event.items():
                if len(cars) < 2:
                    continue

                # sort so leader is highest y position in that lane
                cars.sort(key=lambda c: c.position[1], reverse=True)
                leader = cars[0]
                follower = cars[1]

                # only trigger an event if follower is reasonably close behind
                if follower.position[1] < leader.position[1] - 200.0:
                    leader.desired_speed = vehicle.MAX_VELOCITY * 0.3
                    leader.velocity = min(
                        leader.velocity,
                        leader.desired_speed,
                    )
                    print(f"DEBUG: scripted slow leader {leader.vid} in lane {lane_x}")
                    break

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            running = False

        road.update(dt)

        messages: List[object] = []
        vehicle_states = []

        for i, v in enumerate(road.vehicles):
            x = float(v.position[0])
            y = float(v.position[1])
            speed = float(v.velocity)

            # always send BSM
            messages.append(
                BSM(
                    sender=v.vid,
                    x=x,
                    y=y,
                    speed=speed,
                )
            )
            bsm_count += 1

            # find nearest car ahead in same lane
            ttc = float("inf")
            warning = False

            for j, other in enumerate(road.vehicles):
                if i == j:
                    continue

                same_lane = abs(other.position[0] - v.position[0]) < 1e-3
                ahead = other.position[1] > v.position[1]

                if not (same_lane and ahead):
                    continue

                gap = other.position[1] - v.position[1]

                if gap <= 0.0 or gap < SAFE_DIST:
                    # snap follower back to just behind leader
                    v.position[1] = other.position[1] - SAFE_DIST

                    # don't let follower be faster than leader
                    if v.velocity > other.velocity:
                        v.velocity = other.velocity

                    # strong braking
                    v.acceleration = vehicle.MAX_DECEL
                    warning = True

                    cwm_count += 1
                    messages.append(
                        CWM(
                            sender=v.vid,
                            x=x,
                            y=y,
                            ttc=0.0,
                        )
                    )

                    # leader accelerates away
                    old_v = other.velocity
                    other.velocity = min(
                        other.velocity + 8.0,
                        vehicle.MAX_VELOCITY,
                    )
                    other.acceleration = vehicle.MAX_ACCEL
                    print(
                        f"DEBUG: CLOSE GAP -> CWM from {v.vid}, "
                        f"leader {other.vid} {old_v:.2f}->{other.velocity:.2f}"
                    )
                    ttc = 0.0
                    break

                if v.velocity > other.velocity:
                    rel_speed = v.velocity - other.velocity
                    ttc = gap / max(rel_speed, 1e-3)

                    if ttc < TTC_THRESHOLD:
                        warning = True
                        cwm_count += 1
                        messages.append(
                            CWM(
                                sender=v.vid,
                                x=x,
                                y=y,
                                ttc=ttc,
                            )
                        )

                        # follower brakes
                        v.acceleration = vehicle.MAX_DECEL

                        # leader accelerates away
                        old_v = other.velocity
                        other.velocity = min(
                            other.velocity + 8.0,
                            vehicle.MAX_VELOCITY,
                        )
                        other.acceleration = vehicle.MAX_ACCEL
                        print(
                            f"DEBUG: TTC CWM from {v.vid}, "
                            f"leader {other.vid} {old_v:.2f}->{other.velocity:.2f}, "
                            f"TTC={ttc:.2f}"
                        )
                    # only closest car ahead matters
                    break

            if not warning:
                if v.velocity < v.desired_speed - 0.5:
                    v.acceleration = vehicle.MAX_ACCEL * 0.5
                elif v.velocity > v.desired_speed + 0.5:
                    v.acceleration = vehicle.MAX_DECEL * 0.3
                else:
                    v.acceleration = 0.0

            ttc_for_ui = ttc if ttc != float("inf") else 999.9

            vehicle_states.append(
                {
                    "id": v.vid,
                    "speed": round(speed, 1),
                    "x": x,
                    "y": y,
                    "ttc": ttc_for_ui,
                    "warning": warning,
                }
            )

        lanes: Dict[float, List[vehicle.Vehicle]] = {}
        for car in road.vehicles:
            lane_x = float(car.position[0])
            lanes.setdefault(lane_x, []).append(car)

        for lane_x, cars in lanes.items():
            # sort: leader has largest y
            cars.sort(key=lambda c: c.position[1], reverse=True)
            for idx in range(1, len(cars)):
                leader = cars[idx - 1]
                follower = cars[idx]

                gap = leader.position[1] - follower.position[1]
                if gap < SAFE_DIST:
                    # maintain SAFE_DIST visually
                    follower.position[1] = leader.position[1] - SAFE_DIST

                    # gently slow follower to avoid immediate re-collision
                    if follower.velocity > leader.velocity:
                        follower.velocity = leader.velocity
                        follower.acceleration = min(
                            follower.acceleration,
                            vehicle.MAX_DECEL * 0.5,
                        )

        elapsed = max(sim_time, 1e-3)
        bsm_rate = bsm_count / elapsed
        stats = {
            "vehicles": len(road.vehicles),
            "bsm_rate": round(bsm_rate),
            "cwm_count": cwm_count,
            "latency": avg_latency,
            "packet_loss": packet_loss,
            "vehicle_states": vehicle_states,
        }

        # render
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # TODO: sync these to the emission rate
        freq_accumulator += dt
        if freq_accumulator > message_freq:
            freq_accumulator -= message_freq
            for veh in road.vehicles:
                emitter_renderer.add_instance(200.0, veh.position[0], veh.position[1])
        emitter_renderer.render()

        connected_set = set()
        comm_points = np.array([], dtype=np.float32)
        for i, veh in enumerate(road.vehicles):
            veh_pos3 = [
                float(veh.position[0]),
                float(veh.position[1]),
                np.float32(0.0),
            ]

            sprite_renderer.render(
                sprite,
                car_w,
                car_h,
                translation=veh_pos3,
                scale=[2.0, 2.0],
            )

            for j, other in enumerate(road.vehicles):
                if i != j and (i, j) not in connected_set:
                    if dist(veh.position, other.position) > 300.0:
                        continue

                    other_pos3 = [
                        float(other.position[0]),
                        float(other.position[1]),
                        np.float32(0.0),
                    ]
                    connected_set.add((i, j))
                    connected_set.add((j, i))
                    comm_points = np.append(comm_points, [veh_pos3, other_pos3])

        if comm_points.size > 0:
            line_renderer.render_lines(
                comm_points.astype(np.float32),
                color=[1.0, 1.0, 1.0, 1.0],
            )

        velocity_points = np.array([], dtype=np.float32)
        for veh in road.vehicles:
            vy = float(veh.velocity)
            x0 = float(veh.position[0])
            y0 = float(veh.position[1])
            velocity_points = np.append(
                velocity_points,
                [
                    x0,
                    y0,
                    0.0,
                    x0,
                    y0 + vy * 2.0,
                    0.0,
                ],
            )

        if velocity_points.size > 0:
            line_renderer.render_arrows(
                velocity_points.astype(np.float32),
                color=[0.0, 1.0, 0.0, 1.0],
            )

        draw_stats_panel(stats, window_width, window_height)

        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
