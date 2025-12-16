import math
import argparse

import numpy as np
import pygame as pg
import OpenGL.GL as gl

import highway
import vehicle
from sprite import SpriteRenderer, load_sprite
from emitter import EmitterRenderer
from line import LineRenderer
from ui_statistics import draw_stats_panel


def dist(src, target):
    dx = float(src[0]) - float(target[0])
    dy = float(src[1]) - float(target[1])
    return math.sqrt(dx * dx + dy * dy)


def main(args):
    window_width = 1280
    window_height = 720
    dt = 0.0

    pg.init()
    clock = pg.time.Clock()
    running = True

    road = highway.create_highway(
        num_vehicles=int(args.vehicle_count),
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

    vehicle_scale = float(args.vehicle_scale)

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            running = False

        cwm_count = 0

        # for each vehicle, emit a BSM message to neighbors
        for v in road.vehicles:
            scale = v.emit_bsms(dt, road.vehicles, args.latency, args.packet_loss)
            if scale != 0.0:
                emitter_renderer.add_instance(
                    scale, [0.4, 0.4, 0.4], v.position[0], v.position[1]
                )

        # for each vehicle, emit a CWM message to neighbors when a collision
        # is imminent
        for v in road.vehicles:
            scale = v.emit_cwms(dt, road.vehicles, vehicle_scale, args.latency)
            if scale != 0.0:
                cwm_count += 1
                emitter_renderer.add_instance(
                    scale, [0.6, 0.0, 0.0], v.position[0], v.position[1]
                )

        # bound the vehicles to the height of the highway
        for v in road.vehicles:
            v.update(dt)
            if v.position[1] > road.height / 2.0 + vehicle.VEHICLE_LENGTH / 2.0:
                v.position[1] = -road.height / 2.0 - vehicle.VEHICLE_LENGTH / 2.0

        vehicle_states = []
        for v in road.vehicles:
            vehicle_states.append(
                {
                    "id": v.vid,
                    "speed": round(float(v.velocity), 1),
                    "x": float(v.position[0]),
                    "y": float(v.position[1]),
                }
            )

        stats = {
            "vehicles": len(road.vehicles),
            "bsm_rate": 10,
            "cwm_count": cwm_count,
            "latency": args.latency,
            "packet_loss": float(args.packet_loss) * 100.0,
            "vehicle_states": vehicle_states,
        }

        # render
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        draw_stats_panel(stats, window_width, window_height)
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
                scale=[2.0 * vehicle_scale, 2.0 * vehicle_scale],
            )

            for j, other in enumerate(road.vehicles):
                if i != j and (i, j) not in connected_set:
                    if (
                        veh.position[0] != other.position[0]
                        or dist(veh.position, other.position)
                        > vehicle.BSM_RANGE * vehicle_scale
                    ):
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
                    y0 + vy * 0.5 * vehicle_scale,
                    0.0,
                ],
            )

        if velocity_points.size > 0:
            line_renderer.render_arrows(
                velocity_points.astype(np.float32),
                color=[0.0, 1.0, 0.0, 1.0],
            )

        pg.display.flip()
        dt = float(clock.tick(60)) / 1_000.0

    pg.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Simulates a highway scenario where fully autonomous vehicles \
                communicate with each other to avoid collisions",
    )
    parser.add_argument("-v", "--vehicle-count", default=12)
    parser.add_argument(
        "-s",
        "--vehicle-scale",
        default=1.0,
    )

    parser.add_argument("-l", "--latency", default=30, help="packet latency in ms")
    parser.add_argument(
        "-p", "--packet-loss", default=0.1, help="percentage of packets lost"
    )

    args = parser.parse_args()
    main(args)
