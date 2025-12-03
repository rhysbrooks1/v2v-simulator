import pygame as pg
import numpy as np
import math
import OpenGL.GL as gl
from highway import create_highway
from sprite import SpriteRenderer, load_sprite
from line import LineRenderer


def sine_in_out(t):
    return np.float32(0.5 * (1 - math.cos(math.pi * t)))


def lerp(start, end, t):
    return np.float32(start * (np.float32(1.0) - t) + end * t)


def main():
    window_width = 1280
    window_height = 720

    pg.init()
    dt = 0.0

    clock = pg.time.Clock()
    running = True

    highway = create_highway(10, window_height, window_width / 2)

    # request OpenGL 3.3
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
    pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
    pg.display.set_mode((window_width, window_height), pg.DOUBLEBUF | pg.OPENGL)

    line_renderer = LineRenderer(window_width, window_height)
    sprite_renderer = SpriteRenderer(window_width, window_height)
    sprite, width, height = load_sprite("cars/manual.png")

    while running:
        # input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # update
        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            running = False
        highway.update(dt)

        # render
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        connected_set = set([])
        points = np.array([], dtype=np.float32)
        for i, vehicle in enumerate(highway.vehicles):
            vehicle_translation = [vehicle.position[0], vehicle.position[1], 0.0]
            sprite_renderer.render(
                sprite,
                width,
                height,
                translation=vehicle_translation,
                scale=[2.0, 2.0],
            )
            # for j, other_vehicle in enumerate(highway.vehicles):
            #     if i != j and (i, j) not in connected_set:
            #         other_vehicle_translation = [
            #             other_vehicle.position.x,
            #             other_vehicle.position.y,
            #             0.0,
            #         ]
            #         connected_set.add((i, j))
            #         connected_set.add((j, i))
            #         points = np.append(
            #             points, [vehicle_translation, other_vehicle_translation]
            #         )

        # communication lines
        line_renderer.render_lines(points)

        pg.display.flip()
        dt = float(clock.tick(60)) / 1_000.0

    pg.quit()


if __name__ == "__main__":
    main()
