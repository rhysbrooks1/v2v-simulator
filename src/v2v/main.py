import pygame as pg
import numpy as np
import math
import OpenGL.GL as gl
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
    rot = 0.0

    t1 = 0.0
    s1 = 1.0
    t2 = 1.0
    s2 = -1.0

    clock = pg.time.Clock()
    running = True

    car_translations = [
        np.array([-100.0, 0.0, 0.0], dtype=np.float32),
        np.array([100.0, 0.0, 0.0], dtype=np.float32),
    ]

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

        # render
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        connected_set = set([])
        points = np.array([], dtype=np.float32)
        for i, car_translation in enumerate(car_translations):
            sprite_renderer.render(
                sprite,
                width,
                height,
                translation=car_translation,
                scale=[2.0, 2.0],
                rotation=rot,
            )
            for j, other_car_translation in enumerate(car_translations):
                if i != j and (i, j) not in connected_set:
                    connected_set.add((i, j))
                    connected_set.add((j, i))
                    points = np.append(points, [car_translation, other_car_translation])

        # communication lines
        line_renderer.render_lines(points)

        t1_sample = sine_in_out(t1)
        x1 = lerp(100.0, -100.0, t1_sample)
        t1 += dt * s1
        if t1 > 1.0:
            t1 = 1.0
            s1 = -1.0
        if t1 < 0.0:
            t1 = 0.0
            s1 = 1.0

        t2_sample = sine_in_out(t2)
        x2 = lerp(100.0, -100.0, t2_sample)
        t2 += dt * s2
        if t2 > 1.0:
            t2 = 1.0
            s2 = -1.0
        if t2 < 0.0:
            t2 = 0.0
            s2 = 1.0

        car_translations[0][1] = np.float32(x1)
        car_translations[1][1] = np.float32(x2)

        rot += dt
        pg.display.flip()
        dt = float(clock.tick(60)) / 1_000.0

    pg.quit()


if __name__ == "__main__":
    main()
